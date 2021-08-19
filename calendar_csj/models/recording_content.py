# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
import math
import pytz
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class RecordingContent(models.Model):
    _name = 'recording.content'
    _inherit = ["mail.thread"]
    _description = 'Contenido de Grabaciones'

    name = fields.Char('Nombre del Archivo', required=True, track_visibility='onchange')
    process_id = fields.Many2one('process.process', 'Proceso')
    tag_number = fields.Char('Nombre del Archivo', required=True, track_visibility='onchange')
    content_date = fields.Date('Content Load Date')
    active = fields.Boolean(default=True, help="\
        The active field allows you to hide the class without removing it.", track_visibility='onchange')
    #state = fields.Selection([('Abierto', 'Abierto'), ('Cerrado', 'Cerrado')], 'Estado', default='Abierto', track_visibility='onchange')
    #judge_name = fields.Char('Nombre del Juez', required=True, track_visibility='onchange')
    #appointment_type_id = fields.Many2one('calendar.appointment.type', 'Online Appointment')
    #partner_id = fields.Many2one('res.partner', 'Despacho', ondelete='set null',
    #                             related='appointment_type_id.judged_id')
    #city_id = fields.Many2one('res.city', 'Ciudad', related='partner_id.city_id', track_visibility='onchange')
      # Date