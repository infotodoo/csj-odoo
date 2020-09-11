# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
import math
import pytz
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class CalendarClass(models.Model):
    _name = 'calendar.class'
    _description = 'Calendar class'

    name = fields.Char('Name', required=True)
    active = fields.Boolean(default=True, help="\
        The active field allows you to hide the class without removing it.")
    type = fields.Selection([
        ('audience', 'Audience'),
        ('other', 'Other')], default='audience')

class CalendarHelp(models.Model):
    _name = 'calendar.help'
    _description = 'Ayuda in situ'

    name = fields.Char('Name', required=True)
    active = fields.Boolean(default=True, help="\
        The active field allows you to hide the class without removing it.")
    type = fields.Selection([
        ('support', 'Support in site'),
        ('type_p', 'Participant type'),
        ('type_c', 'Connection type')], default='support')

class CalendarReception(models.Model):
    _name = 'calendar.reception'
    _description = 'Calendar reception'

    name = fields.Char('Name', required=True)
    active = fields.Boolean(default=True)


class CalendarAppointment(models.Model):
    _name = 'calendar.appointment'
    _inherit = ["mail.thread"]
    _description = 'Online Appointment'
    _order = 'appointment_code desc'

    def _default_country_id(self):
        country_id = self.env.ref('base.co')
        return country_id if country_id else False

    def _default_type_id(self):
        type_id = self.env.ref('calendar_csj.calendar_appointment_type')
        return type_id or False

    # def _default_origin_id(self):
    #     partner_id = self.env.user.partner_id
    #     city_id = partner_id.city_id if partner_id else False
    #     return city_id

    def _default_city_id(self):
        partner_id = self.env.user.partner_id
        parent_id = partner_id.parent_id if partner_id else False
        city_id = parent_id.city_id if parent_id else False
        return city_id

    def _default_partner_id(self):
        partner_id = self.env.user.partner_id
        parent_id = partner_id.parent_id if partner_id else False
        return parent_id

    state = fields.Selection([('open','Confirmed'), ('realized','Realized'),
                              ('unrealized','Unrealized'),
                              ('postpone','Postponed'),
                              ('assist_postpone','Assisted and Postponed'),
                              ('assist_cancel','Assisted and Canceled'), ('cancel','Canceled'), ('draft','No confirmed')],
                              'State', default='draft', tracking=True)

    state_copy = fields.Selection([('open','Confirmed'), ('realized','Realized'),
                              ('unrealized','Unrealized'),
                              ('postpone','Postponed'),
                              ('assist_postpone','Assisted and Postponed'),
                              ('assist_cancel','Assisted and Canceled'), ('cancel','Canceled'), ('draft','No confirmed')],
                              'State', default='draft', tracking=True, compute='_get_state')

    # Realizada, Duplicada, No realizada, Asistida aplazada, Asistida cancelada, Cancelada

    state_label = fields.Char(string='Estado en español', compute='_get_state_label', store=False)

    name = fields.Char('Name', default=_('New'))
    active = fields.Boolean('Active', default=True)
    sequence_icsfile_ctl = fields.Integer(string='Sequence ICS File')
    appointment_code = fields.Char(string="Document Code", readonly=True, required=False, copy=False)

    # request_id = fields.Many2one('calendar.request', 'Calendar Request', ondelete='set null') #Solicitud
    type = fields.Selection([
        ('audience','Audience'),
        ('conference','Video conference'),
        ('streaming','Streaming')], 'Request type', default='audience')
    class_id = fields.Many2one('calendar.class', 'Calendar class', ondelete='set null')  # Clase
    help_id = fields.Many2one('calendar.help', 'Calendar help', ondelete='set null')  # Ayuda
    partaker_type = fields.Many2one('calendar.help', 'Portaker Type', ondelete='set null')  # Ayuda
    connection_type = fields.Many2one('calendar.help', 'Connection Type', ondelete='set null')  # Ayuda
    request_date = fields.Date('Request date')  # Date
    appointment_date = fields.Date('Appointment date', default=fields.datetime.now(pytz.timezone("America/Bogota")))  # Date
    appointment_close_date = fields.Date('Close date')
    appointment_close_user_id = fields.Many2one('res.users', 'Close user')  # Date
    appointment_close_user_login = fields.Char('Closing User Login', related='appointment_close_user_id.login', store=False)  # Date
    calendar_type = fields.Selection([('unique', 'Unique'), ('multi', 'Multi')], 'Calendar type', default='unique')  # Agenda
    calendar_datetime = fields.Datetime('Calendar datetime', tracking=True, required=True)  # Fechatag_number
    calendar_date = fields.Date('Calendar date', compute='_compute_calendar_datetime')
    calendar_time = fields.Float('Calendar time', compute='_compute_calendar_datetime')
    calendar_duration = fields.Float('Calendar duration', default=1.00)

    applicant_id = fields.Many2one('res.partner', 'Applicant', ondelete='set null')  # Solicitante
    declarant_id = fields.Many2one('res.partner', 'Declarant', ondelete='set null')  # Declarante
    declarant_text = fields.Text('Declarant input')
    indicted_id = fields.Many2one('res.partner', 'Indicted', ondelete='set null')  # Procesado
    indicted_text = fields.Text('Indicted input')
    applicant_id_label = fields.Char('Applicant Label', compute='_get_applicant_id_label', store=True)

    # Solicitante
    applicant_email = fields.Char('Applicant email', compute='_compute_applicant_id', inverse='_inverse_applicant_id')
    applicant_domain = fields.Char('Applicant domain', compute='_compute_applicant_domain')
    applicant_mobile = fields.Char('Applicant mobile', compute='_compute_applicant_id', inverse='_inverse_applicant_id')

    # origin_id = fields.Many2one('res.city', 'Origin city', ondelete='set null', default=_default_origin_id)
    city_id = fields.Many2one('res.city', 'City', ondelete='set null', related='partner_id.city_id')
    country_state_id = fields.Many2one('res.country.state', 'Country State', related='city_id.state_id')
    partner_id = fields.Many2one('res.partner', 'Judged', domain="[('city_id','=',city_id)]", ondelete='set null',
                                 related='appointment_type_id.judged_id')
    judged_only_code = fields.Char('Partner Only Code', compute="_compute_partner_separated_name", store=False)
    judged_only_name = fields.Char('Partner Only Name', compute="_compute_partner_separated_name", store=True)
    room_id = fields.Many2one('res.judged.room', 'Room', domain="[('partner_id','=',partner_id)]", ondelete='set null')
    room_id_mame = fields.Char('Room Name', related='room_id.virtual_room', store=False)
    partners_ids = fields.Many2many('res.partner', 'appointment_partner_rel', 'appointment_id', 'partner_id', 'Partners')
    partner_ids_label = fields.Char('Partners Label', compute='_get_partner_ids_label', store=True)
    destination_ids = fields.Many2many('res.partner', 'appointment_destination_partner_rel', 'appointment_id', 'partner_id', 'Destinations')
    destination_ids_label = fields.Char('Detinations Label', compute='_get_destination_ids_label', store=True)
    request_type = fields.Selection([('l', 'Free'), ('r', 'Reserved')], 'Request type', default='r')
    request_type_label = fields.Char('Request Type Label', compute='_get_request_type_label', store=False)
    process_number = fields.Char('Process number')
    tag_number = fields.Char('Tag number', compute='_compute_tag_number')
    record_data = fields.Char('Record data', compute='_compute_record_data')
    reception_id = fields.Many2one('calendar.reception', 'Reception medium', ondelete='set null')
    reception_detail = fields.Char('Reception Detail')

    observations = fields.Text('Observations')
    state_description = fields.Text('State description')
    link_streaming = fields.Char('Streaming')
    link_download = fields.Char('Descarga de grabacion')
    link_download_text = fields.Char('Descarga de grabacion tipo text', compute='_get_link_download')
    end_date = fields.Date('Fecha finalizacion')
    end_hour = fields.Float('Hora de finalizacion')

    event_id = fields.Many2one('calendar.event', 'Event', ondelete='set null')
    appointment_type_id = fields.Many2one('calendar.appointment.type', 'Online Appointment', default=_default_type_id)

    lifesize_pin = fields.Char('PIN Lifesize')
    lifesize_uuid = fields.Char('UUID Lifesize')
    lifesize_url = fields.Char('URL Lifesize')
    lifesize_meeting_ext = fields.Char('Lifesize Meeting Ext')
    lifesize_owner = fields.Char('Owner Lifesize')
    lifesize_moderator = fields.Char('Moderator Lifesize')
    lifesize_modified = fields.Boolean('Modified')

    create_uid_login = fields.Char('Create User Login', related='create_uid.login', store=False)
    cw_bool = fields.Boolean('Create/Write', default=False, required=True)

    @api.depends('partners_ids')
    def _get_partner_ids_label(self):
        label = ''
        cont=0
        for partner in self.partners_ids:
            label += '|' if cont else ''
            if partner.email:
                label += str(partner.email)
            cont+=1
        self.partner_ids_label = label


    @api.depends('partner_id')
    def _compute_partner_separated_name(self):
        for record in self:
            code_entity = record.partner_id.entity_id.code if record.partner_id.entity_id else ''
            code_specialty = record.partner_id.specialty_id.code if record.partner_id.specialty_id else ''
            zipcode = record.partner_id.city_id.zipcode if record.partner_id.city_id else ''
            code_city = zipcode or ''
            code = record.partner_id.code or ''
            name = record.partner_id.mame or ''
            record.judged_only_code = code_city + code_entity + code_specialty + code
            record.judged_only_name = name

    @api.depends('destination_ids')
    def _get_destination_ids_label(self):
        label = ''
        cont=0
        for partner in self.destination_ids:
            label += ',' if cont else ''
            label += str(partner.name)
            cont+=1
        self.destination_ids_label = label

    @api.depends('partaker_type','help_id','connection_type')
    def _get_request_type_label(self):
        for record in self:
            record.request_type_label = '%s,%s,%s' % (
                record.partaker_type.name,
                record.help_id.name,
                record.connection_type.name,
            )

    @api.depends('applicant_id')
    def _get_applicant_id_label(self):
        for record in self:
            record.applicant_id_label = '%s - %s - %s' % (
                record.applicant_id.name ,
                record.applicant_id.email if record.applicant_id.email else '',
                record.applicant_id.phone if record.applicant_id.phone else '',
            )

    @api.depends('calendar_datetime')
    def _compute_record_data(self):
        for record in self:
            if record.calendar_datetime:
                tz_offset = self.env.user.tz_offset if self.env.user.tz_offset else False
                tz = int(tz_offset)/100 if tz_offset else 0
                date = record.calendar_datetime + datetime.timedelta(hours=tz) if \
                record.calendar_datetime else False
                res = date.strftime("%Y%m%d_%H%M%S")
                record.record_data = '01_' + res + '_V'

    @api.depends('city_id', 'room_id', 'process_number', 'partner_id', 'request_type', 'record_data')
    def _compute_tag_number(self):
        for record in self:
            if record.city_id and record.city_id.zipcode \
                and (record.room_id or record.type != 'audience') \
                    and record.process_number and record.partner_id \
                        and record.partner_id.entity_id \
                            and record.partner_id.specialty_id \
                                and record.partner_id.code:
                room_code = record.room_id.mame if record.room_id else _(None)
                res = '%s_%s%s%s%s%s%s' % (record.process_number,
                                            str(record.request_type).upper(),
                                            record.city_id.zipcode,
                                            record.partner_id.entity_id.code,
                                            record.partner_id.specialty_id.code,
                                            record.partner_id.code,
                                            room_code)
                if record.record_data:
                    res += '_' + record.record_data
                record.tag_number = res
            else:
                record.tag_number = 'Configurar los valores'


    @api.depends('calendar_datetime')
    def _compute_calendar_datetime(self):
        for record in self:
            # record.write({'state': 'postpone'})
            record.calendar_date = (record.calendar_datetime - datetime.timedelta(hours=5)).date() if \
                record.calendar_datetime else False

            calendar_datetime_timez = record.calendar_datetime - datetime.timedelta(hours=5)

            tz_offset = self.env.user.tz_offset if self.env.user.tz_offset else False
            tz = int(tz_offset)/100 if tz_offset else 0
            if (record.calendar_datetime).hour <5:
                record.calendar_time = (calendar_datetime_timez).hour + \
                record.calendar_datetime.minute/60.0 if \
                record.calendar_datetime else False
            else:
                record.calendar_time = (record.calendar_datetime).hour + tz + \
                record.calendar_datetime.minute/60.0 if \
                record.calendar_datetime else False 

    # @api.depends('appointment_date')
    # def _get_date_today(self):
    #     for record in self:
    #         if record.appointment_date:
    #             record.appointment_date = (record.appointment_date - datetime.timedelta(1)) 


    @api.depends('applicant_id')
    def _compute_applicant_id(self):
        for record in self:
            record.applicant_email = record.applicant_id.email if \
                record.applicant_id else ''
            record.applicant_mobile = record.applicant_id.mobile if \
                record.applicant_id else ''

    @api.depends('applicant_email')
    def _compute_applicant_domain(self):
        for record in self:
            applicant_domain = ''
            if record.applicant_email:
                for email in record.applicant_email.split(','):
                    try:
                        applicant_domain = email.replace(' ', '').split('@')[1]
                    except:
                        applicant_domain = ''
            record.applicant_domain = applicant_domain

    def _inverse_applicant_id(self):
        for record in self:
            if record.applicant_id:
                record.applicant_id.email = record.applicant_email
                record.applicant_id.mobile = record.applicant_mobile
            else:
                continue

   # @api.model
   # def create(self, vals):
        # vals['name'] = vals.get('process_number')[0:23] + 's' + \
        #     self.env['ir.sequence'].next_by_code('calendar.appointment').replace('s','') or _('None')
        # vals['partner_id'] = vals.get('appointment_id')
        # vals['sequence_icsfile_ctl'] = 1
        # vals['appointment_code'] = self.env['ir.sequence'].next_by_code('calendar.appointment.document.number')
        # online_appointment_type = self.env['calendar.appointment.type'].search(
        #     [('id', '=', vals.get('appointment_type_id'))])[0]
        # partner = online_appointment_type.judged_id if online_appointment_type \
        #     and online_appointment_type.judged_id else False
        # # ERROR REPORT THIS JUDGED :C res.partner(11307,), False
        # if partner and partner.permanent_room:
        #     extension = partner.lifesize_meeting_extension if \
        #             partner.lifesize_meeting_extension else False
        #     vals.update({
        #         'lifesize_meeting_ext': extension,
        #         'lifesize_url': 'https://call.lifesizecloud.com/{}'.format(extension) if extension else False,
        #     })
        #     _logger.error('\nSTATUS: NO CREADA EN LIFESIZE {}'.format(vals))
        # else:
        #     vals.update(self.create_lifesize(vals))
        #     _logger.error('\nSTATUS: CREADA EN LIFESIZE {}'.format(vals))
        # res = super(CalendarAppointment, self).create(vals)
        # return res

    @api.model
    def create(self, vals):
        vals["name"] = vals.get("process_number")[0:23] + "s" + self.env[
            "ir.sequence"
        ].next_by_code("calendar.appointment").replace("s", "") or _("None")
        vals["partner_id"] = vals.get("appointment_id")
        vals["sequence_icsfile_ctl"] = 1
        vals["appointment_code"] = self.env["ir.sequence"].next_by_code(
            "calendar.appointment.document.number"
        )
        online_appointment_type = self.env["calendar.appointment.type"].search(
            [("id", "=", vals.get("appointment_type_id"))]
        )[0]
        partner = (
            online_appointment_type.judged_id
            if online_appointment_type and online_appointment_type.judged_id
            else False
        )
        # ERROR REPORT THIS JUDGED :C res.partner(11307,), False
        if partner and partner.permanent_room:
            extension = (
                partner.lifesize_meeting_extension
                if partner.lifesize_meeting_extension
                else False
            )
            vals.update(
                {
                    "lifesize_meeting_ext": extension,
                    "lifesize_url": "https://call.lifesizecloud.com/{}".format(
                        extension
                    )
                    if extension
                    else False,
                }
            )
            _logger.error("\nSTATUS: NO CREADA EN LIFESIZE {}".format(vals))
        else:
            vals.update(self.create_lifesize(vals))
            _logger.error("\nSTATUS: CREADA EN LIFESIZE {}".format(vals))
        res = super(CalendarAppointment, self).create(vals)
        return res

    def write(self, vals):
        if vals.get('calendar_datetime'):
            vals.update(self.write_lifesize(vals))
            vals['sequence_icsfile_ctl'] = self.sequence_icsfile_ctl + 1 if int(self.sequence_icsfile_ctl) else 1
            self.write_event(vals)
        return super(CalendarAppointment, self).write(vals)

    def unlink(self):
        self.unlink_lifesize()
        return super(CalendarAppointment, self).unlink()

    def create_lifesize(self, vals):
        api = {
            'method': 'create',
            'displayName': vals.get('name'),
            'ownerExtension': self.env.user.extension_lifesize or \
                self.env.user.company_id.owner_extension,
            'hiddenMeeting': 'true',
            # 'hiddenMeeting': 'false' if vals.get('request_type') == 'l' else 'true',
        }
        judged_extension_lifesize = False
        if vals.get('appointment_type_id'):
            #SEARCH appointment type
            online_appointment_type = self.env['calendar.appointment.type'].search(
                [('id', '=', vals.get('appointment_type_id'))])[0]
            #SELECT partner from judged_id field
            partner = online_appointment_type.judged_id if online_appointment_type \
                and online_appointment_type.judged_id else False
            if partner and partner.extension_lifesize:
                judged_extension_lifesize = partner.extension_lifesize
        ### moderator and owner rules.
        appointment_type = self.env.user.partner_id.appointment_type
        if appointment_type and appointment_type == 'scheduler':
            api.update({
                'ownerExtension': judged_extension_lifesize or \
                    self.env.user.extension_lifesize or \
                    self.env.user.company_id.owner_extension,
                'moderatorExtension': judged_extension_lifesize or \
                    self.env.user.extension_lifesize or \
                    self.env.user.company_id.owner_extension,
            })
        else:
            api.update({
                #'ownerExtension': self.env.user.company_id.owner_extension,
                'ownerExtension': judged_extension_lifesize or \
                                self.env.user.company_id.owner_extension,
                'moderatorExtension': judged_extension_lifesize or \
                    self.env.user.extension_lifesize or \
                        self.env.user.company_id.owner_extension,
            })
        if vals.get('observations'):
            api.update(description=vals.get('observations'))
        if self.env.user.company_id.lecturer_extension:
            api.update(lecturerExtension=self.env.user.company_id.lecturer_extension)
        # if self.env.user.company_id.moderator_extension:
        #     api.update(moderatorExtension=self.env.user.company_id.moderator_extension)
        resp = self.env['api.lifesize'].api_crud(api)
        dic = self.env['api.lifesize'].resp2dict(resp)
        return dic

    def write_lifesize(self, vals):
        for record in self:
            partner = record.partner_id
            _logger.error('\n{}, {}'.format(partner,partner.permanent_room))
            if partner and not partner.permanent_room:
                description = ("Updated to: %s " % (
                    record.calendar_datetime.strftime("%Y%m%d %H%M%S"))
                    )
                api = {
                    'method': 'update',
                    'description': description,
                    'ownerExtension': record.lifesize_owner,
                    'uuid': record.lifesize_uuid,
                }
                resp = self.env['api.lifesize'].api_crud(api)
                dic = self.env['api.lifesize'].resp2dict(resp)
                dic.update(state='postpone')
            else:
                _logger.error('\nSTATUS: NO MODIFICADA EN LIFESIZE')
                dic = {'state': 'postpone'}
        return dic

    def unlink_lifesize(self):
        for record in self:
            partner = record.partner_id
            _logger.error('\n{}, {}'.format(partner,partner.permanent_room))
            if partner and not partner.permanent_room:
                api = {
                    'method': 'delete',
                    'uuid': record.lifesize_uuid,
                }
                self.env['api.lifesize'].api_crud(api)
            else:
                _logger.error('\nSTATUS: NO CANCELADA EN LIFESIZE')

    def create_event(self, vals):
        dic = {}
        flag = vals.get('cw_bool') or False
        if not flag:
            type_id = self.env['calendar.appointment.type'].browse(vals.get('appointment_type_id'))
            alarm_ids = [(6, 0, type_id.reminder_ids.ids)]
            categ_id = self.env.ref('calendar_csj.calendar_event_type')
            categ_ids = [(4, categ_id.id, False)]
            start_datetime = fields.Datetime.from_string(vals.get('calendar_datetime'))
            stop_datetime = start_datetime + datetime.timedelta(hours=1)
            start_date = start_datetime.date()
            tz_offset = self.env.user.tz_offset if self.env.user.tz_offset else False
            tz = int(tz_offset)/100 if tz_offset else 0
            start_time = start_datetime.hour + tz + start_datetime.minute/60.0
            start_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(start_time * 60, 60))
            room_id = self.env['res.judged.room'].browse(vals.get('room_id'))
            partner_id = room_id.partner_id if room_id else ''
            location = partner_id.street if partner_id else ''
            event = self.env['calendar.event'].sudo().create({
                'state': 'draft',
                'name': _('Appointment: ') + vals.get('name'),
                'start': start_datetime,
                'stop': stop_datetime,
                'start_datetime': start_datetime,
                'stop_datetime': stop_datetime,
                'allday': False,
                'duration': 1.0,
                'description': _('Date: %s \n Time: %s' % (start_date, start_time)),
                'alarm_ids': alarm_ids,
                'appointment_code': self.appointment_code,
                'location': location,
                'partner_ids': vals.get('partners_ids'),
                'categ_ids': categ_ids,
                'appointment_type_id': type_id.id,
                'user_id': self.env.user.id,
                'cw_bool': True,
            })
            dic.update(event_id=event.id)
        return dic

    def create_destiny(self, vals):
        dic = {}
        if vals.get('partners_ids'):
            ids = vals.get('partners_ids')[0][2]
            # if vals.get('applicant_id'):
            #     ids.append(vals.get('applicant_id'))
            if vals.get('destination_id'):
                ids.append(vals.get('destination_id'))
            dic.update(partners_ids=[(6,False,ids)])
        return dic

    def write_event(self, vals):
        # flag = vals.get('cw_bool') or False
        # if not flag:
        for record in self:
            if record.event_id and vals.get('calendar_datetime'):
                start_datetime = fields.Datetime.from_string(vals.get('calendar_datetime'))
                stop_datetime = start_datetime + datetime.timedelta(hours=1)
                dic = {
                    'start_datetime': start_datetime,
                    'stop_datetime': stop_datetime,
                    # 'cw_bool': True,
                }
                record.event_id.write(dic)

    def action_confirm(self):
        self.write({'state': 'open'})
        # self.event_id.write({'state': 'open'})

    def action_cancel(self):
        dic = {'state': 'cancel'}
        self.event_id.write(dic)
        self.event_id.cancel_calendar_event()
        self.state = 'cancel'
        self.write_lifesize(dic)
        #self.write(dic)
        self.unlink_lifesize()

    def action_postpone(self):
        self.write({'state': 'postpone'})

    def float_time_convert(self, float_val):
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        return (factor * int(math.floor(val)), int(round((val % 1) * 60)))

    def export_data(self, fields_to_export):
        """ Override to fix hour format in export file """
        res = super(CalendarAppointment, self).export_data(fields_to_export)
        index = range(len(fields_to_export))
        fields_name = dict(zip(fields_to_export,index))
        try:
            for index, val in enumerate(res['datas']):
                if fields_name.get('calendar_time'):
                    fieldindex = fields_name.get('calendar_time')
                    calendar_time = float(res['datas'][index][fieldindex])
                    hour, minute = self.float_time_convert(calendar_time)
                    res['datas'][index][fieldindex] = '{0:02d}:{1:02d}:00'.format(hour, minute)
                if fields_name.get('request_type'):
                    fieldindex = fields_name.get('request_type')
                    request_type_value = str(res['datas'][index][fieldindex])
                    request_type_value = 'L' if request_type_value == 'Libre' else 'R'
                    res['datas'][index][fieldindex] = request_type_value
        except Exception as e:
            raise UserError('It was not possible to convert the time format when exporting the file.')
        return res

    @api.onchange('state')
    def onchange_state(self):
        if self.state not in  ['cancel','open','draft']:
            self.write({
                'appointment_close_date': datetime.datetime.now(),
                'appointment_close_user_id': self.env.user.id,
            })
        if self.state in ['cancel']:
            self.action_cancel()

    def fetch_calendar_verify_availability(self, calendar_appointment_type_id, date_start, duration):
        timezone = 'America/Bogota'
        #pytz.timezone('UTC')
        tz_session = pytz.timezone(timezone)
        date_start = tz_session.localize(fields.Datetime.from_string(date_start)).astimezone(pytz.utc)
        date_end = date_start + relativedelta(hours=float(duration))
        calendar_appointment_type_obj = self.env['calendar.appointment.type'].browse(int(calendar_appointment_type_id))
        if not calendar_appointment_type_obj.judged_id.calendar_verify_availability(date_start,date_end):
            return False
        return True


    @api.depends('state')
    def _get_state_label(self):
        for record in self:
            if record.state == 'open':
                self.state_label='AGENDADO'
            if record.state == 'realized':
                self.state_label='REALIZADA'
            if record.state == 'unrealized':
                self.state_label='NO REALIZADA'
            if record.state == 'assist_postpone':
                self.state_label='ASISTIDA Y APLAZADA'
            if record.state == 'postpone':
                self.state_label='APLAZADA'
            if record.state == 'assist_cancel':
                self.state_label='ASISTIDA Y CANCELADA'
            if record.state == 'cancel':
                self.state_label='CANCELADO'
            if record.state == 'draft':
                self.state_label='DUPLICADO'


    @api.depends('link_download')
    def _get_link_download(self):
        for record in self:
            if record.link_download:
                record.link_download_text= '"'+ record.link_download + '"'
            else:
                record.link_download_text= False

    @api.depends('state')
    def _get_state(self):
        for record in self:
            record.state_copy=record.state

class CalendarAppointmentType(models.Model):
    _inherit = 'calendar.appointment.type'

    active = fields.Boolean('Active', default=True)
    judged_id = fields.Many2one('res.partner', 'Judged')
    city_id = fields.Many2one('res.city', string='City', related='judged_id.city_id', store=True)
    type = fields.Selection([
        ('audience','Audience'),
        ('conference','Video conference'),
        ('streaming','Streaming')], 'Request type', default='audience')

    applicant_id = fields.Many2one('res.partner', 'Applicant', ondelete='set null')
    declarant_id = fields.Many2one('res.partner', 'Declarant', ondelete='set null')
    indicted_id = fields.Many2one('res.partner', 'Indicted', ondelete='set null')

    request_type = fields.Selection([('l', 'Free'), ('r', 'Reserved')], 'Request type', default='r')
    process_number = fields.Char('Process number')
    reception_id = fields.Many2one('calendar.reception', 'Reception medium', ondelete='set null')

    def search_calendar(self, judged_id):
        res = self.env['calendar.appointment.type'].search([('judged_id','=',judged_id)])
        return res
