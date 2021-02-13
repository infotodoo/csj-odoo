
# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component
from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime
import logging
import json

_logger = logging.getLogger(__name__)


class ParticipantService(Component):
    _inherit = "base.rest.service"
    _name = "res.participant.service"
    _usage = "Participant"
    _collection = "base.rest.csj.odoo.private.services"
    _description = """
        Participant
        Access to the participant services is only allowed to authenticated calendars.
        If you are not authenticated go to <a href='/web/login'>Login</a>
    """



    def search(self, name):
        """
        Buscar Participantes a partir de un ID de agendamiento
        """
        partner_ids = self.env["calendar.appointment"].sudo().search([
            ('appointment_code','=',name),
        ]).partners_ids

        if not partner_ids:
            res = {
                "name": 'No Existen Resultados',
                "email": '',
            }
            return res

        if partner_ids:
            rows = []
            res = {"count": len(partner_ids), "rows": rows}
            for partner in partner_ids:
                _logger.error('--------------------------participants----------------------')
                _logger.error(partner)
                rows.append(self._to_json(partner))
            return res


    def _get(self, _id):
        return self.env["calendar.appointment"].browse(_id)

    def _get_document(self, _id):
        return self.env["calendar.appointment"].browse(_id)

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
            "email": {"type": "string", "required": False, "empty": True},
        }
        return res

    def _validator_return_create(self):
        return self._validator_return_get()



    def _validator_return_update(self):
        return self._validator_return_get()

    def _validator_archive(self):
        return {}

    def _to_json(self, partner):
        res = {
            "name": partner.name,
            "email": partner.email.strip(),
        }
        return res

