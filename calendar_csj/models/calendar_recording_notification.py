# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class CalendarRecordingNotification(models.Model):
    _name = 'calendar.recording.notification'
    _description = 'Calendar Recording Notification'
    _rec_name = 'subject'

    template_id = fields.Many2one('mail.template','Template Email')
    user_id = fields.Many2one('res.users','User to send')
    destinations = fields.Char()
    subject = fields.Char()
    record_name = fields.Char()
    state = fields.Selection([('r','Recived'),('p','Procces'),('s','Send'),('e','Do not Send')])
    token = fields.Char()
    record_url = fields.Char()
    hello = fields.Char()
