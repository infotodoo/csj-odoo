# Part of Odoo, Aktiv Software.
# See LICENSE file for full copyright & licensing details.
import re
from odoo import http
from odoo.http import request


class TeamsAuth(http.Controller):
    """Redirects To Azure Redirect URI and generate access token
    and redirect token for the first time with user Authentication
    with rpc port 15000.
    """

    @http.route(
        ['/azure/auth_success'], type='http', auth="public", website=True)
    def teams_auth(self, **data):
        """After Authorization stores the value of code in user table and
        Push Requesr to get Access Token then redirects to home page.
        """
        user = request.env.user
        user.write({"code": data.get("code")})
        user.generate_user_token()
        host_url = re.sub("azure/auth_success", '', user.company_id.redirect_url)
        return request.redirect(host_url)
