# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    key_lifesize = fields.Char('Token lifesize')
    owner_extension = fields.Char('Owner extension')
    lecturer_extension = fields.Char('Lecturer extension')
    moderator_extension = fields.Char('Moderator extension')


class ResUsers(models.Model):
    _inherit = 'res.users'

    extension_lifesize = fields.Char('Extension Lifesize')
