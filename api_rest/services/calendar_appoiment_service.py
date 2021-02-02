
# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component
from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime
import logging
import json

_logger = logging.getLogger(__name__)


class AppointmentService(Component):
    _inherit = "base.rest.service"
    _name = "calendar.appointment.service"
    _usage = "CalendarAppointment"
    _collection = "base.rest.csj.odoo.private.services"
    _description = """
        Calendar Appointment Services
        Access to the calendar appointment services is only allowed to authenticated calendars.
        If you are not authenticated go to <a href='/web/login'>Login</a>
    """
    
    def get(self, _id):
        """
        Obtener Información de un Agendamiento
        """
        calendar = self.env["calendar.appointment"].browse(_id)
        return self._to_json(calendar)

    def search(self, name):
        """
        Buscar Agendamiento: máximo 80 registros
        """
        appointment_ids = self.env["calendar.appointment"].sudo().search([
            ('appointment_code','like',name)
        ], limit=80)
        
        if appointment_ids:
            rows = []
            res = {"count": len(appointment_ids), "rows": rows}
            for appointment in appointment_ids:
                _logger.error('--------------------------users----------------------')
                _logger.error(appointment)
                #if partner.company_type == 'judged':
                rows.append(self._to_json(appointment))
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
    
    """
    def _validator_return_search(self):
        return {
            "count": {"type": "integer", "required": True},
            "rows": {
                "type": "list",
                "required": True,
                "schema": {"type": "dict", "schema": self._validator_return_get()},
            },
        }
    """

    def _validator_create(self):
        res = {
            "name": {"type": "string", "required": True, "empty": False},
            "type": {"type": "string", "required": False, "empty": True},
            "class_id": {"type": "string", "required": False, "empty": True},
            "help_id": {"type": "string", "required": False, "empty": True},
            "partaker_type": {"type": "string", "required": False, "empty": True},
            "appointment_date": {"type": "string", "required": False, "empty": True},
            
            "applicant": {
                "type": "dict", 
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    "name": {"type": "string"},
                },
                "required": False, "empty": True},
            "city": {
                "type": "dict", 
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    "name": {"type": "string"},
                },
                "required": False, "empty": True},
            
            "country_state": {
                "type": "dict", 
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    "name": {"type": "string"},
                },
                "required": False, "empty": True},
            
            "state": {"type": "string", "required": False, "empty": True},
            "request_date": {"type": "string", "required": False, "empty": True},
            "calendar_date": {"type": "string", "required": False, "empty": True},
            "calendar_time": {"type": "string", "required": False, "empty": True},
            "calendar_datetime": {"type": "string", "required": False, "empty": True},
            "reception_detail": {"type": "string", "required": False, "empty": True},
            "appointment_close": {"type": "string", "required": False, "empty": True},
            "appointment_close_user_id": {"type": "integer", "required": False, "empty": True},
            
            "judged": {
                "type": "dict", 
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    "name": {"type": "string"},
                },
                "required": False, "empty": True},
            
            "room": {
                "type": "dict", 
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    "name": {"type": "string"},
                },
                "required": False, "empty": True},
            
            "entity": {
                "type": "dict", 
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    "name": {"type": "string"},
                },
                "required": False, "empty": True},
            
            "specialty": {
                "type": "dict", 
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    "name": {"type": "string"},
                },
                "required": False, "empty": True},
            
            "participants": {
                "type": "dict", 
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    
                },
                "required": False, "empty": True},
            
            "recordings": {
                "type": "dict", 
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    
                },
                "required": False, "empty": True},
            
            "request_type": {"type": "string", "required": False, "empty": True},
            "process_number": {"type": "string", "required": False, "empty": True},
            "tag_number": {"type": "string", "required": False, "empty": True},
            "room_name": {"type": "string", "required": False, "empty": True},
            "reception_id": {"type": "string", "required": False, "empty": True},
            "observations": {"type": "string", "required": False, "empty": True},
            "applicant_id": {"type": "string", "required": False, "empty": True},
            "applicant_email": {"type": "string", "required": False, "empty": True},
            "applicant_domain": {"type": "string", "required": False, "empty": True},
            "applicant_mobile": {"type": "string", "required": False, "empty": True},
            "record_data": {"type": "string", "required": False, "empty": True},
            "lifesize_meeting_ext": {"type": "string", "required": False, "empty": True},
            "lifesize_url": {"type": "string", "required": False, "empty": True},
            "lifesize_owner": {"type": "string", "required": False, "empty": True},
            "lifesize_moderator": {"type": "string", "required": False, "empty": True},
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

    def _to_json(self, appointment):
        
        
        res = {
            "name": appointment.appointment_code,
            "type": appointment.type,
            "class_id": appointment.class_id.name,
            "help_id": appointment.help_id.name,
            "partaker_type": appointment.partaker_type.name,
            "appointment_date": str(appointment.appointment_date),
            "request_date": str(appointment.request_date),
            "calendar_datetime": str(appointment.calendar_datetime),
            "calendar_time": str(appointment.calendar_time),
            "state": str(appointment.state),
            "reception_detail": appointment.reception_detail,
            "appointment_close_date": appointment.appointment_close_date,
            "appointment_close_user_id": appointment.appointment_close_user_id.id,
            "request_type": appointment.request_type,
            "process_number": appointment.process_number,
            "tag_number": appointment.tag_number,
            "reception_id": appointment.reception_id.name,
            "observations": appointment.observations,
            "applicant_id": appointment.applicant_id.name,
            "applicant_email": appointment.applicant_email,
            "applicant_domain": appointment.applicant_domain,
            "applicant_mobile": appointment.applicant_mobile,
            "record_data": appointment.record_data,
            "lifesize_meeting_ext": appointment.lifesize_meeting_ext,
            "lifesize_url": appointment.lifesize_url,
            "lifesize_owner": str(appointment.lifesize_owner),
            "lifesize_moderator": str(appointment.lifesize_moderator),
            #"partners_ids": appointment.partners_ids,
        }
        if appointment.partner_id.id:
            res["judged"] = {
                "id": appointment.partner_id.judged_only_code,
                "name": appointment.partner_id.name,
            }
            
        if appointment.room_id.id:
            res["room"] = {
                "id": appointment.room_id.id,
                "name": appointment.room_id.name,
            }
        
        if appointment.city_id.id:
            res["city"] = {
                "id": appointment.city_id.id,
                "name": appointment.city_id.name,
            }
            
        if appointment.country_state_id.id:
            res["country_state"] = {
                "id": appointment.country_state_id.id,
                "name": appointment.country_state_id.name,
            }
            
        if appointment.partner_id.entity_id.id:
            res["entity"] = {
                "id": appointment.partner_id.entity_id.id,
                "name": appointment.partner_id.entity_id.name,
            }
            
        if appointment.partner_id.specialty_id.id:
            res["specialty"] = {
                "id": appointment.partner_id.specialty_id.id,
                "name": appointment.partner_id.specialty_id.name,
            }

        
        if appointment.applicant_id.id:
            res["applicant"] = {
                "id": appointment.applicant_id.id,
                "name": appointment.applicant_id.name,
            }
            
        partner_list = []
        partner_list.append({
            'partner_id': appointment.applicant_id.id,
            'partner_name': appointment.applicant_id.name,
            'partner_email': appointment.applicant_id.email.strip(),
            'partner_type': 'applicant',
        })
        if appointment.partners_ids:
            for partner in appointment.partners_ids:
                partner_list.append({
                    'partner_id': partner.id,
                    'partner_name': partner.name,
                    'partner_email': partner.email.strip(),
                    'partner_type': 'guest',
                })
        if appointment.destination_ids:
            for partner in appointment.destination_ids:
                partner_list.append({
                    'partner_id': partner.id,
                    'partner_name': partner.name,
                    'partner_email': partner.email.strip(),
                    'partner_type': 'destination',
                })
        
        res["participants"] = partner_list
        
        recording_list = []
        if appointment.recording_ids:
            for recording in appointment.recording_ids:
                recording_list.append({
                    'name': recording.name,
                    'url': recording.url,
                    'active': str(recording.active),
                    'create_date': str(recording.create_date),
                    'create_user': str(recording.create_uid),
                })
                
        res["recordings"] = recording_list
        return res
