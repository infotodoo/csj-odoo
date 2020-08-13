# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    key_lifesize = fields.Char("Token lifesize")
    owner_extension = fields.Char("Owner extension")
    lecturer_extension = fields.Char("Lecturer extension")
    moderator_extension = fields.Char("Moderator extension")


class ResUsers(models.Model):
    _inherit = "res.users"

    extension_lifesize = fields.Char("Extension Lifesize")
    notification_partner = fields.Many2one("res.partner", "Notification Partner")

    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsers, self).create(vals_list)
        _logger.error(
            f"\nCREATE USER:\nusers_object: {users}\nvals_list: {vals_list}\n"
        )
        return users
