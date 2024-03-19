# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import string

_logger = logging.getLogger(__name__)


class ApiTeams(models.TransientModel):
    _name = "api.teams"
    _description = "Api Teams"

    def api_crud(self, vals):
        token_company = self.env['res.users'].browse(2).teams_access_token
        if not token_company:
            raise ValidationError("Please write token")

        def code(length=4, chars=string.digits):
            return "".join([random.choice(chars) for i in range(length)])

        def api_create(vals):
            """Call Function to generate Teams Meeting link with appropriate
            Time format and time zone if 'teams_link_check' is True.
            """
            active_user = self.env['res.users'].browse(2)
            """Generate Microsoft Teams Meeting link
            Get new Access token if older one is expired
            """
            active_user.refresh_token()
            if active_user.is_authenticated:
                if active_user.token_expire:
                    if active_user.token_expire <= datetime.now():
                        active_user.refresh_token()
                else:
                    raise ValidationError("Generar nuevo token para el agendamiento usando Microsoft Teams.")

            if active_user.teams_refresh_token and not active_user.teams_access_token:
                active_user.refresh_token()
            token = active_user.teams_access_token

            judged_id = self.env['res.partner'].browse(int(vals.get('judged_id')))

            if not active_user.is_authenticated:
                raise ValidationError("Genere un token de acceso para crear una reunión de Microsoft Teams")
            attendees = self.prepare_attendee_vals(vals.get('partner_ids'))

            url = "https://graph.microsoft.com/v1.0/users/" + \
            "{}/calendar/events".format(self.env.user.company_id.client_email)
            header = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(token)
            }
            try:
                description = vals.get("description").replace("\n", " - ")
            except:
                description = vals.get("description")
            payload = {
                "subject": vals.get("displayName"),
                "showAs": vals.get('busy'),
                "body": {
                    "contentType": "HTML",
                    "content": vals.get('description')
                    },
                "start": {
                    "dateTime": vals.get('start'),
                    "timeZone": "UTC"
                    },
                "end": {
                    "dateTime": vals.get('stop'),
                    "timeZone": "UTC"
                    },
                "location": {
                    "displayName": "" if vals.get(
                        'location') in [False, None] else vals.get('location')
                    },
                "hideAttendees": True,
                "participants": {
                    "attendees": [
                        {
                            "upn": judged_id.email,
                            "role": "attendee",
                            "identity": {
                                "user": {
                                    "id": judged_id.name,
                                    "tenantId": "7ea67c76-850a-42c9-9343-64e6c04aaf02",
                                    "identityProvider": "AAD"
                                }
                            }
                        }
                     ]
                },
                "organizer": {
                    "emailAddress": {
                        "name": judged_id.name,
                        "address": judged_id.email
                    },
                },
                "allowNewTimeProposals": True,
                "isOnlineMeeting": True,
                "onlineMeetingProvider": "teamsForBusiness",
                "isAllDay": vals.get('allday')
            }

            try:
                meeting_obj = requests.request(
                    "POST", url, headers=header, json=payload)

            except requests.exceptions.ConnectionError:
                _logger.exception("No se pudo establecer la conexión en %s", url)
                raise ValidationError(
                    _("No se pudo establecer la conexión con Microsoft Teams.")
                    )

            except requests.exceptions.HTTPError:
                _logger.exception(
                    "Invalid API request at %s", url
                    )
                raise ValidationError(
                    _(
                        "Webshipper: Invalid API request at %s",
                        url,
                        )
                    )

            if meeting_obj.status_code in [201, 200]:
                meeting = meeting_obj.json().get('onlineMeeting')
                meeting_content = meeting_obj.json().get('body')
                return {
                    "meeting_body": meeting_content.get(
                        'content') if meeting else '',
                    "meeting_url": meeting.get('joinUrl') if meeting else False,
                    "meeting_id": meeting_obj.json().get(
                        'id') if meeting else False,
                    "action": 'CREATED'
                    }
            else:
                error_body = meeting_obj.json().get('error')
                error_message = "Error creating online meeting link" + \
                    "\nStatus Code: %d \nReason: %s\n" % (
                        meeting_obj.status_code, meeting_obj.reason) + \
                            "Error: %s\nError Message: %s\n" % (
                                error_body.get('code'), error_body.get('message'))

                raise ValidationError(error_message)

        def api_update(values):
            """Update properties of existing Teams Meeting event. only meeting
            organizer(Who enables 'teams_link_check' boolean) can update event.
            """
            active_user = self.env['res.users'].browse(2)
            if self.env.user.is_authenticated:
                if active_user.token_expire:
                    if active_user.token_expire <= datetime.now():
                        active_user.refresh_token()
                else:
                    raise ValidationError("Generate new token for Microsoft teams meeting.")

            if active_user.teams_refresh_token and not active_user.teams_access_token:
                active_user.refresh_token()
            token = active_user.teams_access_token
            update_url = "https://graph.microsoft.com/" + \
                "v1.0/users/{0}/events/{1}".format(self.env.user.company_id.client_email, vals.get('teams_uuid'))

            header = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(token)
                }

            payload = {}
            if values.get('name'):
                payload.update({
                    "subject": values.get('name')
                    })
            if values.get('show_as'):
                payload.update({
                    "showAs": 'busy'
                    })
            if values.get('description'):
                payload.update({
                    "body": {
                        "content": values.get('description'),
                        "contentType": "HTML"
                        }
                    })
            if values.get('start'):
                payload.update({
                    "start": {
                        "dateTime": values.get('start'),
                        "timeZone": "UTC"
                        }
                    })
            if values.get('stop'):
                payload.update({
                    "end": {
                        "dateTime": values.get('stop'),
                        "timeZone": "UTC"
                        }
                    })
            if values.get('location'):
                payload.update({
                    "location": {
                        "displayName": values.get('location')
                        }
                    })
            if 'partner_ids' in values.keys():
                payload.update({
                    "attendees": self.prepare_attendee_vals(
                        values.get('partner_ids'))
                    })

            if payload:
                try:
                    update_response = requests.request(
                        "PATCH", update_url, headers=header, json=payload)

                except requests.exceptions.ConnectionError:
                    _logger.exception(
                        "Could not establish the connection at %s", update_url)
                    raise ValidationError(
                        _("Could not establish the connection.")
                        )

                except requests.exceptions.HTTPError:
                    _logger.exception(
                        "Invalid API request at %s", update_url
                        )
                    raise ValidationError(
                        _(
                            "Webshipper: Invalid API request at %s",
                            update_url,
                            )
                        )

                if update_response.status_code != 200:
                    error_body = update_response.json().get('error')

                    error_message = "Error updating online meeting" + \
                        "\nStatus Code: %d \nReason: %s\n" % (
                            update_response.status_code,
                            update_response.reason) + \
                                "Error: %s\nError Message: %s\n" % (
                                    error_body.get('code'),
                                    error_body.get('message'))

                    raise ValidationError(error_message)


        def api_delete(vals):
            """Delete existing Teams Meeting event.only meeting
            organizer(Who enables 'teams_link_check' boolean) can delete event.
            """
            active_user = self.env['res.users'].browse(2)
            if self.env.user.is_authenticated:
                if active_user.token_expire:
                    if active_user.token_expire <= datetime.now():
                        active_user.refresh_token()
                else:
                    raise ValidationError("Generate new token for Microsoft teams meeting.")
            else:
                raise ValidationError("Generate an access token to delete a Microsoft Teams meeting.")

            if active_user.teams_refresh_token and not active_user.teams_access_token:
                active_user.refresh_token()
            token = active_user.teams_access_token
            delete_url = "https://graph.microsoft.com/" + \
                "v1.0/users/{0}/events/{1}".format(self.env.user.company_id.client_email, vals.get('teams_uuid'))
            header = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(token)
                }
            try:
                delete_response = requests.request(
                    "DELETE", delete_url, headers=header)

            except requests.exceptions.ConnectionError:
                _logger.exception(
                    "Could not establish the connection at %s", delete_url)
                raise ValidationError(
                    _("Could not establish the connection.")
                    )

            except requests.exceptions.HTTPError:
                _logger.exception(
                    "Invalid API request at %s", delete_url
                    )
                raise ValidationError(
                    _(
                        "Webshipper: Invalid API request at %s",
                        delete_url,
                        )
                    )

            if delete_response.status_code != 204:
                error_body = delete_response.json()
                error_message = "Error deleting online meeting" + \
                    "\nStatus Code: %d \nReason: %s\n" % (
                        delete_response.status_code, delete_response.reason) + \
                            "Error: %s\nError Message: %s\n" % (
                                error_body.get('code'), error_body.get('message'))
                raise ValidationError(error_message)


        if vals["method"] == "create":
            return api_create(vals)
        elif vals["method"] == "update":
            return api_update(vals)
        elif vals["method"] == "delete":
            return api_delete(vals)


    def resp2dict(self, resp):
        if resp.get("action") == "UPDATED":
            res = dict(lifesize_modified=True,)
            return res
        elif resp.get("action") == "CREATED":
            res = dict(
                teams_url=resp.get("meeting_url"),
                teams_uuid=resp.get("meeting_id"),
                teams_description=resp.get("meeting_body"),
            )
            return res

    def prepare_attendee_vals(self, values):
        """
        Make a list of dictionary of participant's names and email addresses.
        """
        attendees = []
        res_partner = self.env['res.partner']
        for value in values:
            for partner in value[2]:
                attendees.append(
                    {
                        "emailAddress":
                        {
                            "address": res_partner.browse(partner).email,
                            "name": res_partner.browse(partner).name
                        },
                        "type": "required",
                        #"roles": "owner",
                        }
                    )
        return attendees

