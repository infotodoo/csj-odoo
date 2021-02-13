
# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component
from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime
import logging
import json

_logger = logging.getLogger(__name__)


class EntityService(Component):
    _inherit = "base.rest.service"
    _name = "res.entity.appointment.service"
    _usage = "ResEntity"
    _collection = "base.rest.csj.odoo.private.services"
    _description = """
        Res Entity
        Access to the calendar appointment services is only allowed to authenticated calendars.
        If you are not authenticated go to <a href='/web/login'>Login</a>
    """

    def get(self, _id):
        """
        Obtener Información de una Entidad
        """
        appointment = self.env["res.entity"].browse(_id)
        return self._to_json(appointment)

    def search(self, name):
        """
        Buscar Entidades
        """
        entity_ids = self.env["res.entity"].sudo().search([
        ])

        if entity_ids:
            rows = []
            res = {"count": len(entity_ids), "rows": rows}
            for entity in entity_ids:
                _logger.error('--------------------------users----------------------')
                _logger.error(entity)
                #if partner.company_type == 'judged':
                rows.append(self._to_json(entity))
            return res


    def _get(self, _id):
        return self.env["res.entity"].browse(_id)

    def _get_document(self, _id):
        return self.env["res.entity"].browse(_id)

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

    def _to_json(self, entity):
        res = {
            "id": entity.id,
            "name": entity.mame,
            "code": entity.code,
            "complete_name": entity.name,
        }
        return res
