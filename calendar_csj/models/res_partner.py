# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class ResEntity(models.Model):
    _name = 'res.entity'
    _description = 'Res entity'
    _order = 'code,mame'
    _sql_constraints = [('code_mame_check', 'UNIQUE(code,name)', _("The code have to unique"))]

    code = fields.Char('Code', required=True, size=2)
    mame = fields.Char('Name', required=True) #Epa! what is this Parcos?
    name = fields.Char('Display Name')

    @api.model
    def create(self, vals):
        code = vals.get('code')
        name = vals.get('mame')
        display_name = code + ' ' + name
        vals.update(name=display_name)
        return super(ResEntity, self).create(vals)

    def write(self, vals):
        res = super(ResEntity, self).write(vals)
        if vals.get('code') or vals.get('mame'):
            for record in self:
                code = vals.get('code') or record.code
                name = vals.get('mame') or record.mame
                display_name = code + ' ' + name
                record.name = display_name
        return res

    def search_city(self, var):
        res = self.env['res.city'].sudo().search([('zipcode','=',var)])
        if res:
            return True
        else:
            return False

    def search_speciality(self, var):
        res = self.env['res.specialty'].sudo().search([('code','=',var)])
        if res:
            return True
        else:
            return False

    def search_entity(self, var):
        res = self.env['res.entity'].sudo().search([('code','=',var)])
        if res:
            return True
        else:
            return False

    def search_judged(self, var):
        res = self.env['res.judged'].sudo().search([('code','=',var)])
        if res:
            return True
        else:
            return False

class ResSpecialty(models.Model):
    _name = 'res.specialty'
    _description = 'Res specialty'
    _order = 'code,mame'
    _sql_constraints = [('code_mame_check', 'UNIQUE(code,name,entity_id)', _("The code have to unique"))]

    code = fields.Char('Code', required=True, size=2)
    mame = fields.Char('Name', required=True)
    name = fields.Char('Display Name')
    entity_id = fields.Many2one('res.entity', 'Entity', required=True)

    @api.onchange('mame', 'code', 'entity_id')
    def _onchange_mame(self):
        code_entity = self.entity_id.code if self.entity_id else ''
        name_entity = self.entity_id.mame if self.entity_id else ''
        code = self.code or ''
        name = self.mame or ''
        self.name = code_entity + code + ' ' + name_entity + ' - ' + name

    @api.model
    def create(self, vals):
        entity_id = self.env['res.entity'].browse(vals.get('entity_id'))
        code_entity = entity_id.code
        name_entity = entity_id.mame
        code = vals.get('code')
        name = vals.get('mame')
        display_name = code_entity + code + ' ' + name_entity + ' - ' + name
        vals.update(name=display_name)
        return super(ResSpecialty, self).create(vals)

    def write(self, vals):
        res = super(ResSpecialty, self).write(vals)
        if vals.get('code') or vals.get('mame') or vals.get('entity_id'):
            for record in self:
                entity_id = self.env['res.entity'].browse(vals.get('entity_id'))
                entity_id = entity_id if entity_id else record.entity_id
                code_entity = entity_id.code
                name_entity = entity_id.mame
                code = vals.get('code') or record.code
                name = vals.get('mame') or record.mame
                display_name = code_entity + code + ' ' + name_entity + ' - ' + name
                record.name = display_name
        return res


class ResJudgedRoom(models.Model):
    _name = 'res.judged.room'
    _description = 'Judged room'
    _order = 'code,mame'
    _sql_constraints = [('code_mame_check', 'UNIQUE(code,name,judged_id)', _("The code have to unique"))]

    def _default_country_id(self):
        country_id = self.env.ref('base.co')
        return country_id if country_id else False

    code = fields.Char('Code', required=True)
    mame = fields.Char('Name', required=True)
    name = fields.Char('Display Name')
    virtual_room = fields.Char('Virtual name')
    judged_id = fields.Many2one('res.partner', 'Judged', ondelete='cascade')
    country_id = fields.Many2one('res.country', 'Country', ondelete='set null', default=_default_country_id)
    city_id = fields.Many2one('res.city', 'City')
    active = fields.Boolean('Active', default=True)

    @api.onchange('city_id')
    def _compute_tag_number(self):
        for record in self:
            record.code = record.city_id.zipcode

    @api.model
    def create(self, vals):
        code = vals.get('code') or ''
        name = vals.get('mame')
        display_name = code + ' ' + name
        vals.update(name=display_name)
        return super(ResJudgedRoom, self).create(vals)

    def write(self, vals):
        res = super(ResJudgedRoom, self).write(vals)
        if vals.get('code') or vals.get('mame'):
            for record in self:
                code = vals.get('code') or record.code
                name = vals.get('mame') or record.mame
                display_name = code + ' ' + name
                record.name = display_name
        return res

    def search_city(self,code):
        res = self.env['res.judged.room'].sudo().search([('city_id','=',code)])
        return res

class ResJudged(models.Model):
    _name = 'res.judged'
    _inherit = ["mail.thread"]
    _description = 'Res judged'
    _order = 'code'

    def _default_country_id(self):
        country_id = self.env.ref('base.co')
        return country_id if country_id else False

    code = fields.Char('Code', required=True, size=3)
    mame = fields.Char('Name', required=True)
    entity_id = fields.Many2one('res.entity', 'Entity', related='specialty_id.entity_id')
    specialty_id = fields.Many2one('res.specialty', 'Specialty', required=True)
    country_id = fields.Many2one('res.country', 'Country', ondelete='set null', default=_default_country_id)
    state_id = fields.Many2one('res.country.state', 'State', ondelete='set null', domain="[('country_id','=',country_id)]")
    city_id = fields.Many2one('res.city', 'City', ondelete='set null', domain="[('state_id','=',state_id)]")
    name = fields.Char('Display Name', compute='_compute_mame')
    judged_id = fields.Many2one('res.partner', 'Judged', domain="[('company_type','=','company')]")
    rooms_id = fields.One2many('res.judged.room', 'judged_id', 'Rooms')

    @api.depends('name', 'code', 'city_id', 'city_id.zipcode', 'specialty_id', 'specialty_id.code', 'specialty_id.name', 'entity_id', 'entity_id.code')
    def _compute_mame(self):
        for record in self:
            code_entity = record.entity_id.code if record.entity_id else ''
            code_specialty = record.specialty_id.code if record.specialty_id else ''
            name_specialty = record.specialty_id.mame if record.specialty_id else ''
            zipcode = record.city_id.zipcode if record.city_id else ''
            code_city = zipcode or ''
            code = record.code or ''
            name = record.mame or ''
            record.name = code_city + code_entity + code_specialty + code + ' ' + name_specialty + ' - ' + name


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('company_type','type')
    def _compute_appointment_bool(self):
        for record in self:
            if record.company_type == 'person':
                record.appointment_bool = False
            elif record.type == 'delivery':
                record.appointment_bool = False
            else:
                record.appointment_bool = False

    company_type = fields.Selection([
        ('person', 'Person'),
        ('company', 'Entity'),
        ('judged', 'Judged'),
        ('guest','Guest')], default='person', compute=False, inverse=False)
    type = fields.Selection([
        ('contact', 'Contact'),
        ('invoice', 'Judge'),
        ('delivery', 'Secretary'),
        ('other', 'Other'),
        ('private', '.')], default='contact')
    code = fields.Char('Code', size=3)
    mame = fields.Char('Name')
    extension_lifesize = fields.Char('Extension Lifesize')
    entity_id = fields.Many2one('res.entity', 'Entity', related='specialty_id.entity_id')
    specialty_id = fields.Many2one('res.specialty', 'Specialty')
    rooms_id = fields.One2many('res.judged.room', 'judged_id', 'Rooms')
    hr_employee_id = fields.Many2one('hr.employee', 'Employee')
    appointment_id = fields.Many2one('calendar.appointment.type', 'Appointment')
    appointment_type = fields.Selection([('scheduler','Scheduler'),('secretary','Secretary')], 'Appointment type')
    appointment_user = fields.Many2one('res.users', 'Appointment user')
    appointment_bool = fields.Boolean('Appointment bool', compute='_compute_appointment_bool')
    permanent_room = fields.Boolean('Permanent room', default=False)
    lifesize_meeting_extension = fields.Char('Meeting extension Lifesize')

    @api.onchange('code', 'mame', 'city_id', 'specialty_id', 'entity_id')
    def _onchange_mame(self):
        if self.company_type == 'judged':
            code_entity = self.entity_id.code if self.entity_id else ''
            name_entity = self.entity_id.mame if self.entity_id else ''
            code_specialty = self.specialty_id.code if self.specialty_id else ''
            name_specialty = self.specialty_id.mame if self.specialty_id else ''
            zipcode = self.city_id.zipcode if self.city_id else ''
            code_city = zipcode or ''
            # name_city = record.city_id.name if record.city_id else ''
            code = self.code or ''
            name = self.mame or ''
            self.name = code_city + code_entity + code_specialty + code + ' ' + name_entity + ' - ' + name_specialty + ' - ' + name

    @api.model
    def create(self, vals):
        if vals.get('company_type') and vals.get('company_type') == 'judged':
            vals.update(self.create_hr_calendar(vals))
        res = super(ResPartner, self).create(vals)
        if vals.get('company_type') and vals.get('company_type') == 'judged':
            res.hr_employee_id.write({'judged_id': res.id})
            res.appointment_id.write({'judged_id': res.id})
        if vals.get('company_type') and vals.get('company_type') == 'judged' or vals.get('appointment_type'):
            res.create_res_users(vals)
        return res

    def write(self, vals):
        if 'active' in vals or vals.get('company_type'):
            self.write_hr_calendar(vals)
        return super(ResPartner, self).write(vals)

    def create_hr_calendar(self, vals):
        dic = {}
        # Employee
        # user = self.env.ref('base.template_portal_user_id')
        employee = self.env['hr.employee'].sudo().create({
            'name': vals.get('name'),
        })
        dic.update(hr_employee_id=employee.id)
        # Calendar Type
        alarm = self.env.ref('calendar.alarm_notif_1')
        appointment = self.env['calendar.appointment.type'].sudo().create({
            'name': vals.get('name'),
            'appointment_duration': 0.5,
            'reminder_ids': [(6,False,[alarm.id])],
            'employee_ids': [(6,False,[employee.id])],
            'slot_ids': self.create_appointment_slot(),
            'location': vals.get('street'),
            'is_published': True,
        })
        dic.update(appointment_id=appointment.id)
        return dic

    def write_hr_calendar(self, vals):
        for record in self:
            if 'active' in vals:
                if record.hr_employee_id:
                    record.hr_employee_id.write({'active': vals.get('active')})
                if record.appointment_id:
                    record.appointment_id.write({'active': vals.get('active')})
            if vals.get('company_type') == 'judged':
                if not record.hr_employee_id and not record.appointment_id:
                    record.write(self.create_hr_calendar({'name': record.name}))
                else:
                    if record.hr_employee_id:
                        record.hr_employee_id.write({'active': True})
                    if record.appointment_id:
                        record.appointment_id.write({'active': True})

    def create_appointment_slot(self):
        lis = []
        date = [8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 14, 14.5, 15, 15.5, 16, 16.5, 17, 17.5]
        for i in range(1, 6):
            for j in date:
                lis.append((0,0,{'weekday': str(i), 'hour': j}))
        return lis

    def create_res_users(self, vals):
        group = self.env.ref('base.group_portal')
        user = self.env['res.users'].sudo().create({
            'name': self.name,
            'partner_id': self.id,
            'login': self.email or str(self.id),
            'active': True,
            'groups_id': [(6,0,[group.id])]
        })
        if vals.get('company_type') and vals.get('company_type') == 'judged':
            self.hr_employee_id.write({'user_id': user.id})
        self.appointment_user = user

    def search_company_type(self):
        res = self.env['res.partner'].sudo().search([('company_type','=','judged')])
        return res

    def calendar_verify_availability(self, date_start, date_end):
        """ verify availability of the partner(s) between 2 datetimes on their calendar
        """
        if bool(self.env['calendar.event'].search_count([
            ('partner_ids', 'in', self.ids),
            ('state', 'not in', ['cancel',]),
            '|', '&', ('start_datetime', '<', fields.Datetime.to_string(date_end)),
                      ('stop_datetime', '>', fields.Datetime.to_string(date_start)),
                 '&', ('allday', '=', True),
                      '|', ('start_date', '=', fields.Date.to_string(date_end)),
                           ('start_date', '=', fields.Date.to_string(date_start))])):
            return False
        return True

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    judged_id = fields.Many2one('res.partner', 'Judged')
