# Part of Odoo, Aktiv Software.
# See LICENSE file for full copyright & licensing details.
from odoo import models, fields


class ResCompany(models.Model):
    """Azure Application Credentials
    """
    _inherit = "res.company"

    supported_account_types = fields.Selection([
        ('single_tenant', 'Accounts in this organizational directory only(Singal tenant)'),
        ('multitenant', 'Accounts in any organizational directory (Any Azure AD directory - Multitenant)')],
                                               default='single_tenant',
                                               string="Supported account types")
    client_code = fields.Char(string="Client ID",
                              help="Azure Application ID")
    secret_code = fields.Char(string="Secret Value",
                              help="Azure Secret Value\
                                  (create secret from Azure Application)")
    tenant_code = fields.Char(string="Tenant ID",
                              help="Azure Application's Directory ID")
    redirect_url = fields.Char(string="Redirect URI",
                               compute="_compute_redirect_url",
                               help="[ODOO-URL]/azure/auth_success")

    def _compute_redirect_url(self):
        system_config = self.env['ir.config_parameter']
        base_url = system_config.search([('key', '=', 'web.base.url')]).value
        redirect_url = base_url + "/azure/auth_success"
        self.write({
            "redirect_url": redirect_url
        })
