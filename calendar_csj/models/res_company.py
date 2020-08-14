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
    uuid_lifesize = fields.Char("UUID Lifesize")
    notification_partner = fields.Many2one("res.partner", "Notification Partner")

    @api.model_create_multi
    def create(self, vals_list):
        for i in range(len(vals_list)):
            user = vals_list[i]
            portal_flag = False
            if not user.get("sel_groups_1_8_9"):
                try:
                    # From res.partner the portal user only have 'groups_id': [(6, 0, [8])] like a portal identifier
                    group_8 = user.get("groups_id")
                    portal_flag = 8 == group_8[0][-1][0]
                except:
                    pass
            else:
                try:
                    portal_flag = user.get("sel_groups_1_8_9") == 8
                except:
                    pass

            if user.get("sel_groups_1_8_9") and portal_flag:
                # Search user and if exist fill fields and if not create and fill fields
                try:
                    api = {"method": "search", "email": user.get("login")}
                    resp = self.env["api.lifesize"].api_user_crud(api)
                    vals_list[i]["extension_lifesize"] = resp["userObject"]["extension"]
                    vals_list[i]["uuid_lifesize"] = resp["userObject"]["UUID"]
                    _logger.error(f"\nSEARCH LIFESIZE OK: {user}\n{vals_list}")
                except ValueError:
                    api = {
                        "method": "create",
                        "email": user.get("login"),
                        "name": user.get("name"),
                    }
                    resp = self.env["api.lifesize"].api_user_crud(api)
                    vals_list[i]["extension_lifesize"] = resp["userObject"]["extension"]
                    vals_list[i]["uuid_lifesize"] = resp["userObject"]["UUID"]
                    _logger.error(f"\nCREATE LIFESIZE OK: {user}\n{vals_list}")
                except:
                    _logger.error(
                        f"\nSOMETING WENT WRONG LIFESIZE: {user}\n{vals_list}"
                    )
                    pass
        users = super(ResUsers, self).create(vals_list)
        _logger.error(
            f"\nCREATE USER:\nusers_object: {users}\nvals_list: {vals_list}\n"
        )
        return users

    def unlink(self):
        for id in self.ids:
            user = self.env["res.users"].browse(id)
            if user and user.uuid_lifesize and self.env.user.company_id.key_lifesize:
                api = {
                    "method": "delete",
                    "uuid": user.uuid_lifesize,
                }
                try:
                    resp = self.env["api.lifesize"].api_user_crud(api)
                    if resp["success"]:
                        _logger.error(f"\nDELETE LIFESIZE OK")
                    else:
                        _logger.error(f"\nDELETE LIFESIZE WRONG: {resp}")
                except:
                    _logger.error(f"\nDELETE LIFESIZE WRONG")
                    pass
        return super(ResUsers, self).unlink()
