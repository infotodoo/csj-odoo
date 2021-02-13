# -*- coding: utf-8 -*-
# from odoo import http


# class SmtpByUser(http.Controller):
#     @http.route('/smtp_by_user/smtp_by_user/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smtp_by_user/smtp_by_user/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smtp_by_user.listing', {
#             'root': '/smtp_by_user/smtp_by_user',
#             'objects': http.request.env['smtp_by_user.smtp_by_user'].search([]),
#         })

#     @http.route('/smtp_by_user/smtp_by_user/objects/<model("smtp_by_user.smtp_by_user"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smtp_by_user.object', {
#             'object': obj
#         })
