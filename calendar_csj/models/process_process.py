# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import math
import pytz
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class ProcessProcess(models.Model):
    _name = 'process.process'
    _inherit = ["mail.thread"]
    _description = 'Procesos'
    _order = 'id desc'

    name = fields.Char('Número de Proceso', required=True, track_visibility='onchange')
    active = fields.Boolean(default=True, help="\
        The active field allows you to hide the class without removing it.", track_visibility='onchange')
    state = fields.Selection([('Abierto', 'Abierto'), ('Cerrado', 'Cerrado')], 'Estado', default='Abierto', track_visibility='onchange')
    appointment_type_id = fields.Many2one('calendar.appointment.type', 'Online Appointment')
    partner_id = fields.Many2one('res.partner', 'Despacho', ondelete='set null', related='appointment_type_id.judged_id', store=True, track_visibility='onchange')
    applicant_id = fields.Many2one('res.partner', 'Solicitante', ondelete='set null', track_visibility='onchange')  # Solicitante
    declarant_id = fields.Many2one('res.partner', 'Declarante', ondelete='set null', track_visibility='onchange')  # Declarante
    declarant_text = fields.Text('Declarant input', track_visibility='onchange')
    indicted_id = fields.Many2one('res.partner', 'Procesado', ondelete='set null', track_visibility='onchange')  # Procesado
    indicted_text = fields.Text('Indicted input', track_visibility='onchange')
    create_uid_login = fields.Char('Usuario creación', related='create_uid.login', store=False, track_visibility='onchange')
    appointment_ids = fields.One2many('calendar.appointment', 'process_id', 'Agendamientos', track_visibility='onchange')
    recording_content_ids = fields.One2many('recording.content', 'process_id', 'Contenido Grabaciones', track_visibility='onchange')
    partner_ids = fields.One2many('res.partner', compute='_compute_partner_ids', string='Agendamientos', track_visibility='onchange')
    applicant_email = fields.Char('Solicitante Email')
    applicant_domain = fields.Char('Solicitante Dominio', track_visibility='onchange')
    applicant_mobile = fields.Char('Solicitante Celular', track_visibility='onchange')
    city_id = fields.Many2one('res.city', 'City', related='partner_id.city_id', store=True, track_visibility='onchange')
    country_state_id = fields.Many2one('res.country.state', 'Country State', related='city_id.state_id', track_visibility='onchange')
    #judge_id = fields.Many2one('res.partner', 'Juez', domain="[('type', '=', 'invoice')]")
    judge_name = fields.Char('Nombre del Juez', required=True, track_visibility='onchange')
    tag_number = fields.Char('Etiqueta', compute='_compute_tag_number', store=True)
    request_type = fields.Selection([('l', 'Libre'), ('r', 'Reservado')], 'Tipo de Audiencia', default='r')
    process_datetime = fields.Datetime('Fecha y Hora de Realización', tracking=True, required=True)


    @api.depends('appointment_ids')
    def _compute_partner_ids(self):
        for rec in self:
            rec.partner_ids.unlink()
            for appointment in rec.appointment_ids:
                rec.partner_ids += appointment.partners_ids


    @api.depends('city_id', 'appointment_ids', 'name', 'partner_id', 'appointment_type_id', 'process_datetime')
    def _compute_tag_number(self):
        for record in self:
            if record.city_id and record.city_id.zipcode \
                    and record.name and record.partner_id \
                        and record.partner_id.entity_id \
                            and record.partner_id.specialty_id \
                                and record.partner_id.code:
                #room_code = record.room_id.mame if record.room_id else _(None)
                """Se fija sala acordada con jonathan leon"""
                room_obj = self.env['res.judged.room'].browse(11693)
                res = '%s_%s%s%s%s%s%s' % (record.name,
                                            str(record.request_type).upper(),
                                            record.city_id.zipcode,
                                            record.partner_id.entity_id.code,
                                            record.partner_id.specialty_id.code,
                                            record.partner_id.code,
                                            room_obj.mame)
                tz_offset = self.env.user.tz_offset if self.env.user.tz_offset else False
                tz = int(tz_offset)/100 if tz_offset else 0
                date = record.process_datetime
                date_txt = date.strftime("%Y%m%d_%H%M%S")
                cont = 1
                for c in record.recording_content_ids:
                    cont+=1
                if len(str(cont)) == 1:
                    cont = '0' + str(cont)
                else:
                    cont = str(cont)

                record_data = cont + '_' + date_txt + '_V'
                if record_data:
                    res += '_' + record_data
                record.tag_number = res


    @api.model
    def fetch_process_exist(self, process_number):
        response = []
        if not process_number:
            return False
        process_obj = self.env['process.process'] .search([('name', '=', process_number)])
        if process_obj:
            #return True, process_obj.city_id.name, process_obj.appointment_type_id.name, process_obj.judge_id.name
            return True, process_obj.city_id.name, process_obj.city_id.id, process_obj.appointment_type_id.name, process_obj.tag_number
        else:
            if len(process_number) != 23:
                return False, 'failed length'
            city = self.env['res.entity'].sudo().search_city(process_number[0:5])
            entity = self.env['res.entity'].sudo().search_entity(process_number[5:7])
            speciality = self.env['res.entity'].sudo().search_speciality(process_number[7:9])
            rad_year = process_number[12:16]
            year = datetime.now()
            year_limit = int(year.strftime("%Y")) + 1

            if not city or not entity or not speciality:
                return False, 'failed composition'
            if not int(rad_year) in range(1900,year_limit):
                return False, 'failed composition'
            else:
                return False

    @api.model
    def fetch_scheduler_default_data(self):
        partner = self.env.user.partner_id
        judged_id = None
        response = []
        if partner.appointment_type != 'scheduler':
            judged_id = partner.parent_id
            if judged_id:
                return True, judged_id.city_id.name, judged_id.city_id.id, self.env['calendar.appointment.type'].sudo().search_calendar(judged_id.id)[0].name
                #suggested_appointment_types = request.env['calendar.appointment.type'].sudo().search_calendar(judged_id.id)
            else:
                return False
        else:
            return False


    @api.model
    def process_create_from_add_content(self, process_number, city_id, calendar_appointment_type_id, judge_name, process_datetime, tag_number, request_type, prepare_file):
        if len(process_number) != 23:
            return False, 'La longitud del proceso no es correcta!.'

        appointment_obj = self.env['calendar.appointment.type'].browse(int(calendar_appointment_type_id))
        city = self.env['res.entity'].sudo().search_city(process_number[0:5])
        entity = self.env['res.entity'].sudo().search_entity(process_number[5:7])
        speciality = self.env['res.entity'].sudo().search_speciality(process_number[7:9])
        rad_year = process_number[12:16]
        year = datetime.now()
        year_limit = int(year.strftime("%Y")) + 1
        if city and entity and speciality:
            if not int(rad_year) in range(1900,year_limit):
                return False, 'La estructura del número del proceso no es correcta!.'
        else:
            return False, 'La estructura del número del proceso no es correcta!.'

        if request_type == 'Libre':
            request_type = 'l'
        else:
            request_type = 'r'

        process_obj = self.env['process.process'].search([('name', '=', process_number)])
        if not process_obj:
            """Creando un nuevo proceso"""
            try:
                process_values = {
                    'name': process_number,
                    'active': True,
                    'state': 'Abierto',
                    'appointment_type_id': int(calendar_appointment_type_id),
                    'city_id': int(city_id),
                    'judge_name': judge_name,
                    'process_datetime': process_datetime,
                    'request_type': request_type,
                    #'recording_content_ids': [0,0, recording_content_ids]
                }
                new_process = self.env['process.process'].sudo().create(process_values)
                if new_process:
                    recording_content_ids = {
                        'name': prepare_file,
                        'process_id': new_process.id,
                        'tag_number': new_process.tag_number,
                        'content_date': new_process.process_datetime,
                        'active': True,
                    }
                    new_process.sudo().write({
                        'recording_content_ids': [(0,0, recording_content_ids)],
                        #'process_datetime': new_process.process_datetime + relativedelta(hours=5)
                    })
            except Exception as e:
                return False, str(e)
            else:
                return True, new_process.name
        else:
            """Actualizando proceso existente"""
            try:
                process_values = {
                    'active': True,
                    'state': 'Abierto',
                    'appointment_type_id': int(calendar_appointment_type_id),
                    'city_id': int(city_id),
                    'judge_name': judge_name,
                    'process_datetime': process_datetime,
                    'request_type': request_type,
                }
                process_obj.sudo().write(process_values)
                recording_content_ids = {
                    'name': prepare_file,
                    'process_id': process_obj.id,
                    'tag_number': process_obj.tag_number,
                    'content_date': process_obj.process_datetime,
                    'active': True
                }
                process_obj.sudo().write({
                    'recording_content_ids': [(0,0, recording_content_ids)],
                    #'process_datetime': process_obj.process_datetime + relativedelta(hours=5)
                })
            except Exception as e:
                return False, str(e)
            else:
                return True, process_obj.name
