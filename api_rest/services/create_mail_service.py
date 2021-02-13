
# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component
from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime
import logging
import json

_logger = logging.getLogger(__name__)


class MailService(Component):
    _inherit = "base.rest.service"
    _name = "mail.service"
    _usage = "Mail"
    _collection = "base.rest.csj.odoo.private.services"
    _description = """
        Mail Services
        Access to the mail services is only allowed to authenticated partners.
        If you are not authenticated go to <a href='/web/login'>Login</a>
    """

    def get(self, _id):
        """
        Get mail's informations
        """
        mail = self.env["calendar.recording.notification"].browse(_id)
        return self._to_json(mail)

    def search(self, name):
        """
        Searh mail by name
        """
        mails = self.env["calendar.recording.notification"].name_search(name)
        mails = self.env["calendar.recording.notification"].browse([i[0] for i in mails])
        rows = []
        res = {"count": len(mails), "rows": rows}
        for mail in mails:
            rows.append(self._to_json_search(mail))
        return res

    def _get(self, _id):
        return self.env["calendar.recording.notification"].browse(_id)

    def _get_document(self, _id):
        return self.env["calendar.recording.notification"].browse(_id)

    def create(self, **params):
        """
        Create a new notification
        """
        _logger.error('*********************')
        _logger.error('*********************')
        notification_vals_list = []
        notification_vals = params


        #notification_vals['name'] = invoice_lines
        notification = self.env['calendar.recording.notification'].sudo().create(notification_vals)
        return self._to_json(notification)

    def _validator_update(self):
        res = self._validator_create()
        for key in res:
            if "required" in res[key]:
                del res[key]["required"]
        return res

    # Validator
    def _validator_return_get(self):
        res = self._validator_create()
        res.update({"id": {"type": "integer", "required": True, "empty": False}})
        return res

    def _validator_search(self):
        return {"name": {"type": "string", "nullable": False, "required": True}}

    def _validator_return_search(self):
        return {
            "count": {"type": "integer", "required": False},
            "rows": {
                "type": "list",
                "required": False,
                "schema": {"type": "dict", "schema": self._validator_return_get()},
            },
        }

    def _validator_create(self):
        res = {
            "token": {"type": "string", "required": False, "empty": True},
            "user_id": {"type": "integer", "required": False, "empty": True},
            "template_id": {"type": "integer", "required": False, "empty": True},
            "subject": {"type": "string", "required": False, "empty": True},
            "destinations": {"type": "string", "required": False, "empty": True},
            "record_name": {"type": "string", "required": False, "empty": True},
            "record_url": {"type": "string", "required": False, "empty": True},
            "hello": {"type": "string", "required": False, "empty": True}
        }
        return res

    def _validator_return_create(self):
        return self._validator_return_get()

    def _validator_return_update(self):
        return self._validator_return_get()

    def _validator_archive(self):
        return {}

    def _to_json(self, mail):
        if mail.id:
            return {
                'id': mail.id,
                'type': 'OK',
                'name': 'Notificación Creada Exitosamente!',
            }
        else:
            return {
                'id': 0,
                'type': 'ERROR',
                'name': 'Ocurrio un error al crear la notificación!',
            }

    def _to_json_search(self, mail):
        res = {
            "name": mail.name,
            "subject": mail.subject,
            "user_id": mail.user_id.id,
            "template_id": mail.template_id.id,
            "destinations": mail.destinations,
            "record_name": mail.record_name,
            "record_url": mail.record_url,
            "hello": mail.hello
        }
        return res
