# Part of Odoo, Aktiv Software.
# See LICENSE file for full copyright & licensing details.
import logging
from datetime import datetime, timedelta
import requests
from odoo import models, fields, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Users(models.Model):
    """Authorize User, Get Access Token and Refresh
    access token if access token is expired.
    """
    _inherit = "res.users"

    is_authenticated = fields.Boolean()
    teams_access_token = fields.Char(string="Microsoft Teams Token")
    teams_refresh_token = fields.Char()
    token_expire = fields.Datetime(string="Expires In")
    code = fields.Char(readonly=True)
    has_permission_download_report = fields.Boolean(string='Tiene permiso para descargar el reporte?')

    def authorize_teams_credentials(self):
        """Redirects to Azure Authorization Url with all required perameters.
        'teams_auth' controller is called.
        """
        redirect_uri = self.sudo().company_id.redirect_url
        scope = "https://graph.microsoft.com/Calendars.ReadWrite " + \
                "https://graph.microsoft.com/OnlineMeetings.ReadWrite " + \
                "https://graph.microsoft.com/openid " + \
                "https://graph.microsoft.com/User.Read " + \
                "offline_access"

        auth_perameter = "?client_id={0}&response_type=code&redirect_uri={1}&response_mode=query&scope={2}&state=12345".format(
            self.company_id.client_code,
            redirect_uri, scope)

        if self.company_id.supported_account_types == 'single_tenant':
            authorization_uri = "https://login.microsoftonline.com/" + \
                "{0}/oauth2/v2.0/authorize".format(
                    self.company_id.tenant_code,) + auth_perameter
        else:
            authorization_uri = "https://login.microsoftonline.com/organizations/oauth2/v2.0/authorize" + auth_perameter
        return {
            'type': 'ir.actions.act_url',
            'url': authorization_uri,
            'target': 'new'
            }

    def generate_user_token(self):
        """Post Request to Get Access token and Refresh token.
        """
        redirect_uri = self.sudo().company_id.redirect_url
        scope = "https://graph.microsoft.com/Calendars.ReadWrite " + \
                "https://graph.microsoft.com/OnlineMeetings.ReadWrite " + \
                "https://graph.microsoft.com/User.Read " + \
                "offline_access openid"

        if self.company_id.supported_account_types == 'single_tenant':
            tenant = self.company_id.tenant_code
            token_url = "https://login.microsoftonline.com/" + \
                "{}/oauth2/v2.0/token".format(tenant)
        else:
            token_url = "https://login.microsoftonline.com/" + \
                "organizations/oauth2/v2.0/token"
        client_body = {
            "client_id": self.company_id.client_code,
            "scope": scope,
            "code": self.code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "client_secret": self.company_id.secret_code
            }
        try:
            acc_token = requests.post(token_url, data=client_body)

        except requests.exceptions.ConnectionError:
            _logger.exception("Could not establish the connection at %s", token_url)
            raise ValidationError(
                _("Could not establish the connection.")
                )

        except requests.exceptions.HTTPError:
            _logger.exception(
                "Invalid API request at %s", token_url
                )
            raise ValidationError(
                _(
                    "Webshipper: Invalid API request at %s",
                    token_url,
                    )
                )

        if acc_token.status_code == 200:
            expires_in = acc_token.json().get("ext_expires_in")
            self.write({
                "is_authenticated": True,
                "teams_access_token": acc_token.json().get("access_token"),
                "teams_refresh_token": acc_token.json().get("refresh_token"),
                "token_expire": datetime.now() + timedelta(
                    seconds=expires_in - 300)
                })
        else:
            response_error = acc_token.json()
            error_body = acc_token.json().get('error')
            if isinstance(error_body, str):
                error_message = "Error getting 'Access token' " + \
                    "\nStatus Code: %d \nReason: %s\n" % (
                        acc_token.status_code, acc_token.reason) + \
                            "Error: %s\nError URI: %s\n" % (
                                response_error.get('error_description'),
                                response_error.get('error_uri') if response_error.get('error_uri') else None)
            else:
                error_message = "Error getting 'Access token' " + \
                    "\nStatus Code: %d \nReason: %s\n" % (
                        acc_token.status_code, acc_token.reason) + \
                            "Error: %s\nError Message: %s\n" % (
                                error_body.get('code'), error_body.get('message'))
            raise ValidationError(error_message)

    def refresh_token(self):
        """Post a request to get an access token
        with a refresh token without authentication.
        """
        redirect_uri = self.sudo().company_id.redirect_url
        scope = "https://graph.microsoft.com/Calendars.ReadWrite " + \
                "https://graph.microsoft.com/OnlineMeetings.ReadWrite " + \
                "https://graph.microsoft.com/User.Read " + \
                "offline_access openid"

        if self.company_id.supported_account_types == 'single_tenant':
            tenant = self.company_id.tenant_code
            token_url = "https://login.microsoftonline.com/" + \
                "{}/oauth2/v2.0/token".format(tenant)
        else:
            token_url = "https://login.microsoftonline.com/" + \
                "organizations/oauth2/v2.0/token"

        client_body = {
            "client_id": self.company_id.client_code,
            "scope": scope,
            "refresh_token": self.teams_refresh_token,
            "redirect_uri": redirect_uri,
            "grant_type": "refresh_token",
            "client_secret": self.company_id.secret_code
            }
        if self.teams_refresh_token:
            try:
                acc_token = requests.post(token_url, data=client_body)
            except requests.exceptions.ConnectionError:
                _logger.exception(
                    "Could not establish the connection at %s", token_url)
                raise ValidationError(
                    _("Could not establish the connection.")
                    )

            except requests.exceptions.HTTPError:
                _logger.exception(
                    "Invalid API request at %s with data", token_url
                    )
                raise ValidationError(
                    _(
                        "Webshipper: Invalid API request at %s",
                        token_url,
                        )
                    )
            if acc_token.status_code == 200:
                expires_in = acc_token.json().get("ext_expires_in")
                self.write({
                    "teams_access_token": acc_token.json().get("access_token"),
                    "teams_refresh_token": acc_token.json().get(
                        "refresh_token"),
                    "token_expire": datetime.now() + timedelta(
                        seconds=expires_in - 10)})
            else:
                response_error = acc_token.json()
                error_body = response_error.get('error')
                if isinstance(error_body, str):
                    error_message = "Error getting 'Refresh token' " + \
                        "\nStatus Code: %d \nReason: %s\n" % (
                            acc_token.status_code, acc_token.reason) + \
                                "Error: %s\nError URI: %s\n" % (
                                    response_error.get('error_description'),
                                    response_error.get(
                                        'error_uri') if response_error.get(
                                            'error_uri') else None)
                else:
                    error_message = "Error getting 'Refresh token' " + \
                        "\nStatus Code: %d \nReason: %s\n" % (
                            acc_token.status_code, acc_token.reason) + \
                                "Error: %s\nError Message: %s\n" % (
                                    error_body.get('code'), error_body.get('message'))
                raise ValidationError(error_message)