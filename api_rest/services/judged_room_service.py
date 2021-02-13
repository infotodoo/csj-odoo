
# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component
from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime
import logging
import json

_logger = logging.getLogger(__name__)


class JudgedRoomService(Component):
    _inherit = "base.rest.service"
    _name = "res.judged.room.service"
    _usage = "JudgedRoom"
    _collection = "base.rest.csj.odoo.private.services"
    _description = """
        Res Judged Room
        Access to the Res Judged Room services is only allowed to authenticated calendars.
        If you are not authenticated go to <a href='/web/login'>Login</a>
    """

    def get(self, _id):
        """
        Obtener Información de una Sala
        """
        room = self.env["res.judged.room"].browse(_id)
        return self._to_json(room)

    def search(self, name):
        """
        Buscar Salas
        """
        room_ids = self.env["res.judged.room"].sudo().search([
            ('active','=',True),
            ('judged_id','!=',False),
        ])

        if room_ids:
            rows = []
            res = {"count": len(room_ids), "rows": rows}
            for room in room_ids:
                _logger.error('--------------------------specialties----------------------')
                _logger.error(room)
                #if partner.company_type == 'judged':
                rows.append(self._to_json(room))
            return res


    def _get(self, _id):
        return self.env["res.judged.room"].browse(_id)

    def _get_document(self, _id):
        return self.env["res.judged.room"].browse(_id)

    # Validator
    def _validator_return_get(self):
        res = self._validator_create()
        res.update({"id": {"type": "integer", "required": False, "empty": False}})
        return res

    def _validator_search(self):
        return {"name": {"type": "string", "nullable": False, "required": True}}


    def _validator_return_search(self):
        return {
            "count": {"type": "integer", "required": True},
            "rows": {
                "type": "list",
                "required": True,
                "schema": {"type": "dict", "schema": self._validator_return_get()},
            },
        }

    def _validator_create(self):
        res = {
            "name": {"type": "string", "required": True, "empty": False},
            "code": {"type": "string", "required": False, "empty": True},
            "complete_name": {"type": "string", "required": False, "empty": True},
            "virtual_room": {"type": "string", "required": False, "empty": True},
            "judged_id": {"type": "string", "required": False, "empty": True},
            "judged_name": {"type": "string", "required": False, "empty": True},
            "city_id": {"type": "integer", "required": False, "empty": True},
            "city_name": {"type": "string", "required": False, "empty": True},
        }
        return res

    def _validator_return_create(self):
        return self._validator_return_get()

    def _validator_update(self):
        res = self._validator_create()
        for key in res:
            if "required" in res[key]:
                del res[key]["required"]
        return res

    def _validator_return_update(self):
        return self._validator_return_get()

    def _validator_archive(self):
        return {}

    def _to_json(self, room):
        res = {
            #"id": calendar.id,
            "name": room.mame,
            "code": str(room.code),
            "complete_name": room.name if room.name else '',
            "virtual_room": room.name if room.name else '',
            "judged_id": str(room.judged_id.judged_only_code),
            "judged_name": room.judged_id.name if room.judged_id.name else '',
            "city_id": room.city_id.id,
            "city_name": room.city_id.name if room.city_id.name else '',
        }
        return res
