# -*- coding: utf-8 -*-
from odoo.addons.web.controllers import main
from odoo.http import request
from odoo.exceptions import Warning
import odoo
import odoo.modules.registry
from odoo.tools.translate import _
from odoo import http

import logging

_logger = logging.getLogger(__name__)


class Home(main.Home):

    @http.route('/web/login', type='http', auth="public")
    def web_login(self, redirect=None, **kw):
        main.ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            ip_address = request.httprequest.environ['REMOTE_ADDR']

            _logger.error('*********************************************************************************************')
            _logger.error(ip_address)

            banned_ips = [
                '66.102.8.173',
                '66.102.8.171',
                '66.102.8.173',
                '66.249.83.66',
                '66.249.83.100',
                '190.217.19.156',
                '66.102.8.175',
                '190.217.24.4'
            ]
            if ip_address in banned_ips:
                request.uid = old_uid
                values['error'] = _("Not allowed to login from this IP")

            if request.params['login']:
                user_rec = request.env['res.users'].sudo().search(
                    [('login', '=', request.params['login'])])
                try:
                    uid = request.session.authenticate(
                        request.session.db,
                        request.params[
                            'login'],
                        request.params[
                            'password'])
                    request.params['login_success'] = True
                    return http.redirect_with_hash(
                        self._login_redirect(uid, redirect=redirect))
                except odoo.exceptions.AccessDenied as e:
                    request.uid = old_uid
                    if e.args == odoo.exceptions.AccessDenied().args:
                        values['error'] = _("Wrong login/password")


        return request.render('web.login', values)