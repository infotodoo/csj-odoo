# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component
from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime
import logging
import json

_logger = logging.getLogger(__name__)


class UserService(Component):
    _inherit = "base.rest.service"
    _name = "user.service"
    _usage = "Users"
    _collection = "base.rest.csj.odoo.private.services"
    _description = """
        User Services
        Access to the partner services is only allowed to authenticated partners.
        If you are not authenticated go to <a href='/web/login'>Login</a>
    """

    def get(self, _id):
        """
        Obtener Información de un Usuario
        """
        user_id = self.env["res.users"].browse(_id)
        if not user_id:
            return {
                    'id': 41,
                    'type': 'ERROR',
                    'name': 'Usuario No Existe!',
                    'judged': '',
                }
        #user_id = self.env["res.users"].search[('id','=',_id)]
        partner_id = self.env['res.partner'].search([('id','=',user_id.partner_id.id)], limit=1).filtered(lambda line: line.appointment_type in ('scheduler','secretary'))
        if partner_id:
            return self._to_json(user_id)
        return {
                    'id': 41,
                    'type': 'ERROR',
                    'name': 'Usuario No Existe!',
                    'judged': '',
                }


    def search(self, name):
        """
        Buscar Usuarios por Nombre: busqueda limitada a 80 resultados
        """

        #partner_ids = self.env["res.partner"].name_search(name)
        #partner_ids = self.env["res.partner"].search([('name','like',name)], limit=80).filtered(lambda line: line.appointment_type in ('scheduler','secretary'))
        partner_ids = self.env["res.partner"].search([('name','like',name),('company_type', '=', 'judged')], limit=80)
        _logger.error('--------------------------111users----------------------')
        _logger.error(partner_ids)
        if partner_ids:
            rows = []
            res = {"count": len(partner_ids), "rows": rows}
            for partner in partner_ids:
                _logger.error('--------------------------users----------------------')
                _logger.error(partner)
                #if partner.company_type == 'judged':
                rows.append(self._to_json_partner(partner))
            return res




    def _get(self, _id):
        user_id = self.env["res.users"].browse(_id)
        if not user_id:
            return {
                    'id': 41,
                    'type': 'ERROR',
                    'name': 'Usuario No Existe!',
                    'judged': '',
                }
        #user_id = self.env["res.users"].search[('id','=',_id)]
        partner_id = self.env['res.partner'].search([('id','=',user_id.partner_id.id)], limit=1).filtered(lambda line: line.appointment_type in ('scheduler','secretary'))
        if partner_id:
            return user_id
        return {
                    'id': 41,
                    'type': 'ERROR',
                    'name': 'Usuario No Existe!',
                    'judged': '',
                }
        #return self.env["res.users"].browse(_id)

    def _get_document(self, _id):
        user_id = self.env["res.users"].browse(_id)
        if not user_id:
            return {
                    'id': 41,
                    'type': 'ERROR',
                    'name': 'Usuario No Existe!',
                    'judged': '',
                }
        #user_id = self.env["res.users"].search[('id','=',_id)]
        partner_id = self.env['res.partner'].search([('id','=',user_id.partner_id.id)], limit=1).filtered(lambda line: line.appointment_type in ('scheduler','secretary'))
        if partner_id:
            return user_id
        return {
                    'id': 41,
                    'type': 'ERROR',
                    'name': 'Usuario No Existe!',
                    'judged': '',
                }
        #return self.env["res.users"].browse(_id)

    # Validator
    def _validator_return_get(self):
        res = self._validator_create()
        res.update({"id": {"type": "integer", "required": True, "empty": False}})
        return res

    def _validator_search(self):
        return {
            "name": {"type": "string", "nullable": False, "required": False},
            #"type": {"type": "string", "required": False, "empty": True},
            #"judged": {"type": "string", "required": False, "empty": True},
            #"judged_code": {"type": "string", "required": False, "empty": True},
            #"office": {"type": "string", "required": False, "empty": True},
            #"entity_name": {"type": "string", "required": False, "empty": True},
            #"specialty_name": {"type": "string", "required": False, "empty": True},
            #"email": {"type": "string", "required": False, "empty": True},
            #"name_complete": {"type": "string", "required": False, "empty": True},
        }


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
            "name": {"type": "string", "required": False, "empty": True},
            "type": {"type": "string", "required": False, "empty": True},
            "judged": {"type": "string", "required": False, "empty": True},
            "judged_id": {"type": "string", "required": False, "empty": True},
            "office": {"type": "string", "required": False, "empty": True},
            "entity_name": {"type": "string", "required": False, "empty": True},
            "specialty_name": {"type": "string", "required": False, "empty": True},
            "email": {"type": "string", "required": False, "empty": True},
            "name_complete": {"type": "string", "required": False, "empty": True},
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

    def _to_json(self, user_id):
        res = {
            "id": user_id.id,
            "name": user_id.name,
            "type": str(user_id.partner_id.appointment_type),
            'judged': str(user_id.partner_id.parent_id.name),
            "judged_id": user_id.partner_id.parent_id.judged_only_code if user_id.partner_id.parent_id else '',
            "office": user_id.partner_id.parent_id.mame if user_id.partner_id.parent_id.mame else '',
            "entity_name": user_id.partner_id.parent_id.entity_id.name if user_id.partner_id.parent_id.entity_id.name else '',
            "specialty_name": user_id.partner_id.parent_id.specialty_id.mame if user_id.partner_id.parent_id.specialty_id.mame else '',
            "email": user_id.partner_id.parent_id.email.strip() if user_id.partner_id.parent_id.email else '',
            "name_complete": user_id.partner_id.parent_id.contact_address_complete if user_id.partner_id.parent_id.contact_address_complete else '',
        }
        return res

    def _to_json_partner(self, partner_id):
        res = {
            "id": partner_id.id,
            "name": partner_id.name,
            "type": str(partner_id.appointment_type),
            'judged': str(partner_id.parent_id.name),
            "judged_id": partner_id.parent_id.cojudged_only_codede if partner_id.parent_id.judged_only_code else '',
            "office": partner_id.parent_id.mame if partner_id.parent_id.mame else '',
            "entity_name": partner_id.parent_id.entity_id.name if partner_id.parent_id.entity_id.name else '',
            "specialty_name": partner_id.parent_id.specialty_id.mame if partner_id.parent_id.specialty_id.mame else '',
            "email": partner_id.parent_id.email.strip() if partner_id.parent_id.email else '',
            "name_complete": partner_id.parent_id.contact_address_complete if partner_id.parent_id.contact_address_complete else '',
        }
        return res
