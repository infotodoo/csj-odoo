# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz
from babel.dates import format_datetime, format_date

from werkzeug.urls import url_encode
from datetime import datetime

from odoo import http, fields, _
from odoo.http import request
from odoo.tools import html2plaintext, DEFAULT_SERVER_DATETIME_FORMAT as dtf
from odoo.tools.misc import get_lang
from odoo.addons.website_calendar.controllers.main import WebsiteCalendar
from odoo.exceptions import ValidationError

import json
from odoo import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


class WebsiteCalendarInherit(WebsiteCalendar):
    @http.route([
        '/website/calendar',
        '/website/calendar/<model("calendar.appointment.type"):appointment_type>',
    ], type='http', auth="public", website=True)
    def calendar_appointment_choice(self, appointment_type=None, employee_id=None, message=None, types=None, **kwargs):
        partner = request.env.user.partner_id
        judged_id = None
        if partner.appointment_type != 'scheduler':
            judged_id = partner.parent_id
            if judged_id:
                suggested_appointment_types = request.env['calendar.appointment.type'].sudo().search_calendar(judged_id.id)
            else:
                return request.render("website_calendar.setup", {'message':'unassigned_partner'})
            if not suggested_appointment_types:
                return request.render("website_calendar.setup", {'message': 'unassigned_origin', 'judged': judged_id.name})
                #raise ValidationError('Ningún origen asosiado a %s.' % judged_id.name)
            appointment_type = suggested_appointment_types[0]
        else:
            if not appointment_type:
                country_code = request.session.geoip and request.session.geoip.get('country_code')
                if country_code:
                    suggested_appointment_types = request.env['calendar.appointment.type'].search([
                        '|', ('country_ids', '=', False),
                            ('country_ids.code', 'in', [country_code])])
                else:
                    suggested_appointment_types = request.env['calendar.appointment.type'].search([])

                if not suggested_appointment_types:
                    return request.render("website_calendar.setup", {})
                appointment_type = suggested_appointment_types[0]
            else:
                suggested_appointment_types = appointment_type

        return request.render("website_calendar.index", {
            'appointment_type': appointment_type,
            'suggested_appointment_types': suggested_appointment_types,
            'message': message,
            'types': types,
            'calendar_appointment_type_id': partner.id if partner.appointment_type != 'scheduler' else 1,
            'city_name': partner.city,
            'judged_name': judged_id.name if judged_id else '',
        })

    @http.route(['/website/calendar/get_appointment_info'], type='json', auth="public", methods=['POST'], website=True)
    def get_appointment_info(self, appointment_id, prev_emp=False, types=False, **kwargs):
        Appt = request.env['calendar.appointment.type'].browse(int(appointment_id)).sudo()
        result = {
            'message_intro': Appt.message_intro,
            'assignation_method': Appt.assignation_method,
        }
        if result['assignation_method'] == 'chosen':
            selection_template = request.env.ref('website_calendar.employee_select')
            result['employee_selection_html'] = selection_template.render({
                'appointment_type': Appt,
                'suggested_employees': Appt.employee_ids.name_get(),
                'selected_employee_id': prev_emp and int(prev_emp),
                'types':types,
            })
        return result

    # @http.route(['/website/calendar/<model("calendar.appointment.type"):appointment_type>/appointment'], type='http', auth="public", website=True)
    # def calendar_appointment(self, appointment_type=None, employee_id=None, timezone=None, failed=False, types=False, **kwargs):
    #     #### TYPESSS 4 robot
    #     request.session['timezone'] = timezone or appointment_type.appointment_tz
    #     if not employee_id:
    #         employee_id = appointment_type.employee_ids[0] # Employee No. 1
    #     Employee = request.env['hr.employee'].sudo().browse(int(employee_id)) if employee_id else None
    #     Slots = appointment_type.sudo()._get_appointment_slots(request.session['timezone'], Employee)
    #     return request.render("website_calendar.appointment", {
    #         'appointment_type': appointment_type,
    #         'timezone': request.session['timezone'],
    #         'failed': failed,
    #         'slots': Slots,
    #         'types': types
    #     })

    @http.route(['/website/calendar/<model("calendar.appointment.type"):appointment_type>/info'], type='http', auth="public", website=True)
    #def calendar_appointment_form(self, appointment_type, employee_id, date_time, types=False, **kwargs):
    def calendar_appointment_form(self, appointment_type, date_time, duration, types=False, **kwargs):
        #timezone = self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'
        #timezone = pytz.timezone(self.event_tz) if self.event_tz else pytz.timezone(self._context.get('tz') or 'UTC')
        request.session['timezone'] = appointment_type.appointment_tz or 'UTC'
        # partner_data = {}
        # if request.env.user.partner_id != request.env.ref('base.public_partner'):
        #     partner_data = request.env.user.partner_id.read(fields=['name', 'mobile', 'email'])[0]

        request.session['timezone'] = appointment_type.appointment_tz
        #day_name = format_datetime(datetime.strptime(date_time, dtf), 'EEE', locale=get_lang(request.env).code)
        day_name = format_datetime(datetime.strptime(date_time, "%Y-%m-%d %H:%M"), 'EEE', locale=get_lang(request.env).code)
        #date_formated = format_datetime(datetime.strptime(date_time, dtf), locale=get_lang(request.env).code)
        date_formated = format_datetime(datetime.strptime(date_time, "%Y-%m-%d %H:%M"), locale=get_lang(request.env).code)
        city_code = appointment_type.judged_id.city_id.id
        employee_id = appointment_type.judged_id.hr_employee_id.id
        employee_obj = request.env['hr.employee'].sudo().browse(int(employee_id))
        timezone = request.session['timezone']
        tz_session = pytz.timezone(timezone)
        date_start = tz_session.localize(fields.Datetime.from_string(date_time)).astimezone(pytz.utc)
        date_end = date_start + relativedelta(hours=float(duration))

        # check availability calendar.event with partner of appointment_type
        if appointment_type and appointment_type.judged_id:
            if not appointment_type.judged_id.calendar_verify_availability(date_start,date_end):
                return request.render("website_calendar.index", {
                    'appointment_type': appointment_type,
                    'suggested_appointment_types': request.env['calendar.appointment.type'].sudo().search([('id','=',appointment_type.id)]),
                    'message': 'already_scheduling',
                    'date_start': date_start,
                    'date_end': date_end,
                    'types': types,
                })

        if types[0] == 'A':
            suggested_class = request.env['calendar.class'].sudo().search([('type','=','audience')])
        else:
            suggested_class = request.env['calendar.class'].sudo().search([('type','=','other')])
        suggested_help1 = request.env['calendar.help'].sudo().search([('type','=','support')])
        suggested_help2 = request.env['calendar.help'].sudo().search([('type','=','type_p')])
        suggested_help3 = request.env['calendar.help'].sudo().search([('type','=','type_c')])
        suggested_rooms = request.env['res.judged.room'].sudo().search_city(city_code)
        suggested_partners = request.env['res.partner'].sudo().search([])
        #suggested_companies = request.env['res.partner'].sudo().search_company_type()
        suggested_reception = request.env['calendar.reception'].sudo().search([])
        return request.render("website_calendar.appointment_form", {
            #'partner_data': partner_data,
            'appointment_type': appointment_type,
            'suggested_class': suggested_class,
            'suggested_partners': suggested_partners,
            #'suggested_companies': suggested_companies,
            'suggested_reception': suggested_reception,
            'suggested_rooms': suggested_rooms,
            'suggested_help1': suggested_help1,
            'suggested_help2': suggested_help2,
            'suggested_help3': suggested_help3,
            'types': types,
            'duration': duration,
            'datetime': date_time,
            'datetime_locale': day_name + ' ' + date_time,
            'datetime_str': date_time,
            'employee_id': employee_id,
            'duration': duration,
            'countries': request.env['res.country'].search([]),
        })

    @http.route(['/website/calendar/<model("calendar.appointment.type"):appointment_type>/submit'], type='http', auth="public", website=True, method=["POST"])
    def calendar_appointment_submit(self, appointment_type, datetime_str, employee_id, types, class_id, reception_detail,
                                    reception_id, process_number, request_type, duration, request_date, connection_type,
                                    room_id, help_id, name, email, phone, guestcont, destinationcont, partaker_type,
                                    declarant_text=False, indicted_text=False, description=False,
                                    country_id=False, **kwargs):


        timezone = request.session['timezone']
        tz_session = pytz.timezone(timezone)
        date_start = tz_session.localize(fields.Datetime.from_string(datetime_str)).astimezone(pytz.utc)
        # date_end = date_start + relativedelta(hours=float(duration))#appointment_type.appointment_duration)
        request_date = datetime.strptime(request_date, '%Y-%m-%d').date()
        duration = float(duration)
        if len(phone) > 10:
            return ValidationError('Número de telefono %s no permitido.' % phone )
        date_end = date_start + relativedelta(hours=duration)
        domain_emails = [ "cendoj.ramajudicial.gov.co",
                          "cortesuprema.ramajudicial.gov.co",
                          "consejoestado.ramajudicial.gov.co",
                          "consejosuperior.ramajudicial.gov.co",
                          "deaj.ramajudicial.gov.co",
                          "fiscalia.gov.co",
                          "axede.com.co",
                          "corteconstitucional.gov.co",
        ]
        if email.split('@')[-1] not in domain_emails:
            return request.render("website_calendar.appointment_form", {
                'appointment_type': appointment_type,
                'message': 'process_email_failed',
                'date_start': date_start,
                'duration': duration,
                'types': types,
            })
            #return ValidationError('Dominio @%s no permitido.' % email.split('@')[-1] )

        # check availability of the employee again (in case someone else booked while the client was entering the form)
        Employee = request.env['hr.employee'].sudo().browse(int(employee_id))
        """
        if Employee.user_id and Employee.user_id.partner_id:
            if not Employee.user_id.partner_id.calendar_verify_availability(date_start, date_end):
                return request.redirect('/website/calendar/%s/appointment?failed=employee' % appointment_type.id)
        """

        # check availability calendar.event with partner of appointment_type
        if appointment_type and appointment_type.judged_id:
            if not appointment_type.judged_id.calendar_verify_availability(date_start,date_end):
                return request.render("website_calendar.appointment_form", {
                    'appointment_type': appointment_type,
                    'message': 'already_scheduling',
                    'date_start': date_start,
                    'date_end': date_end,
                    'types': types,
                })

        if types:
            if types[0] == 'A':
                if len(process_number) != 23:
                    # return {
                    #         'type': 'ir.actions.client',
                    #         'tag': 'display_notification',
                    #         'params': {
                    #             'title': _('Success'),
                    #             'message': _('Longitud del Número de proceso no permitida.'),
                    #             'sticky': False,
                    #             }}
                    return request.render("website_calendar.appointment_form", {
                        'appointment_type': appointment_type,
                        'message': 'process_longer_failed',
                        'date_start': date_start,
                        'duration': duration,
                        'types': types,
                    })
                    #raise ValidationError('Longitud del Número de proceso no permitida.')
                city = request.env['res.entity'].sudo().search_city(process_number[0:5])
                entity = request.env['res.entity'].sudo().search_entity(process_number[5:7])
                speciality = request.env['res.entity'].sudo().search_speciality(process_number[7:9])
                # judged = request.env['res.entity'].sudo().search_judged(process_number[9:12])
                rad_year = process_number[12:16]
                year = datetime.now()
                year_limit = int(year.strftime("%Y")) + 1
                # logger.info("\ncity:{}{}\nentity:{}{}\nspeciality:{}{}\njudged:{}{}\nyear:{}\n".format(
                """
                logger.info("\ncity:{}{}\nentity:{}{}\nspeciality:{}{}\nyear:{}\n".format(
                    process_number[0:5], city,
                    process_number[5:7], entity,
                    process_number[7:9], speciality,
                    # process_number[9:12], judged,
                    int(rad_year) in range(year_limit))
                )
                """
                # if city and entity and speciality and judged:
                if city and entity and speciality:
                    if not int(rad_year) in range(1900,year_limit):
                        return request.render("website_calendar.appointment_form", {
                            'appointment_type': appointment_type,
                            'message': 'process_longer_failed',
                            'date_start': date_start,
                            'duration': duration,
                            'types': types,
                        })
                        #raise ValidationError('Número de proceso ERRONEO.')
                else:
                    return request.render("website_calendar.appointment_form", {
                        'appointment_type': appointment_type,
                        'message': 'process_longer_failed',
                        'date_start': date_start,
                        'duration': duration,
                        'types': types,
                    })
                    #raise ValidationError('Número de proceso ERRONEO.')
        else:
            raise ValidationError('Tipo de agendamiento de la cita no encontrado.')
        country_id = int(country_id) if country_id else None
        partner_ids = []
        Partner = request.env['res.partner'].sudo().search([('email', '=like', email)], limit=1)

        if Partner:
            """
            if not Partner.calendar_verify_availability(date_start, date_end):
                return request.redirect('/website/calendar/%s/appointment?failed=partner' % appointment_type.id)
            """
            if not Partner.mobile or len(Partner.mobile) <= 5 and len(phone) > 5:
                Partner.write({'mobile': phone})
            if not Partner.country_id:
                Partner.country_id = country_id
        else:
            Partner = Partner.create({
                'name': name,
                'email': email,
                'mobile': phone,
                'company_type': 'guest',
            })

        for i in range(1,int(guestcont)):
            name_n = kwargs['nameguest%s'%i] if kwargs['nameguest%s'%i] != '' else False
            email_n = kwargs['emailguest%s'%i] if kwargs['emailguest%s'%i] != '' else False
            if email_n and name_n:
                partner_n = request.env['res.partner'].sudo().search([('email', '=like', email_n)], limit=1)
                """
                if partner_n:

                    if not partner_n.calendar_verify_availability(date_start, date_end):
                        return request.redirect('/website/calendar/%s/appointment?failed=partner' % appointment_type.id)
                else:
                """
                if not partner_n:
                    partner_n = partner_n.create({
                        'name': name_n,
                        'email': email_n,
                        'company_type': 'guest',
                    })
                partner_ids.append(partner_n.id)
            else:
                pass

        destination_ids = []
        for i in range(1,int(destinationcont)):
            destination_name = kwargs['destino%s'%i] if kwargs['destino%s'%i] != '' else False
            destination_id = destination_name.split(" - ")
            destination_obj = request.env['res.partner'].sudo().search([('id', '=', destination_id[0])])
            destination_ids.append(destination_obj.id)


        class_id = int(class_id)
        reception_id = int(reception_id)
        applicant_id = appointment_type.judged_id.id if appointment_type.judged_id else False
        #destination_id = int(destination_id)
        destination_id = None
        partner_ids.append(Partner.id)
        request_type = 'r' if request_type[0] == 'R' else 'l'
        if destination_id:
            partner_ids.append(destination_id)
        if applicant_id:
            partner_ids.append(applicant_id)
        else:
            partner_ids.append(Partner.id)

        # include email copy for appointment user creation
        useremail_obj = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        if useremail_obj.notification_partner:
            partner_obj = request.env['res.partner'].sudo().search([('email', '=', useremail_obj.notification_partner.email)], limit=1)
            partner_ids.append(partner_obj.id)

        partner_ids = [(6,False,partner_ids)]

        # Descripcion
        description = description
        for question in appointment_type.question_ids:
            key = 'question_' + str(question.id)
            if question.question_type == 'checkbox':
                answers = question.answer_ids.filtered(lambda x: (key + '_answer_' + str(x.id)) in kwargs)
                description += question.name + ': ' + ', '.join(answers.mapped('name')) + '\n'
            elif kwargs.get(key):
                if question.question_type == 'text':
                    description += '\n' + question.name + '\n' + kwargs.get(key, False) + '\n\n'
                else:
                    description += question.name + ': ' + kwargs.get(key) + '\n'
        categ_id = request.env.ref('website_calendar.calendar_event_type_data_online_appointment')
        alarm_ids = appointment_type.reminder_ids and [(6, 0, appointment_type.reminder_ids.ids)] or []
        event = request.env['calendar.event'].sudo().create({
            'state': 'open',
            'name': _('%s with %s') % (appointment_type.name, process_number),
            'start': date_start.strftime(dtf),
            'start_date': date_start.strftime(dtf),
            'start_datetime': date_start.strftime(dtf),
            'stop': date_end.strftime(dtf),
            'stop_datetime': date_end.strftime(dtf),
            'allday': False,
            'duration': duration,
            'description': description,
            'alarm_ids': alarm_ids,
            'location': appointment_type.location,
            'types': types,
            'partner_ids': partner_ids,
            'destination_ids': destination_ids,
            'categ_ids': [(4, categ_id.id, False)],
            'appointment_type_id': appointment_type.id,
            'user_id': Employee.user_id.id,
            'class_id' : class_id,
            'reception_id' : reception_id,
            'reception_detail' : reception_detail,
            'indicted_text' : indicted_text,
            'declarant_text' : declarant_text,
            'applicant_id' : Partner.id,
            'destination_id' : destination_id,
            'process_number' : process_number,
            'request_type' : request_type,
            'request_date' : request_date,
            'room_id': room_id,
            'help_id': help_id,
            'partaker_type': partaker_type,
            'connection_type': connection_type,
        })
        event.attendee_ids.write({'state': 'accepted'})
        return request.redirect('/website/calendar/view/' + event.access_token + '?message=new')


class OdooWebsiteSearchAppointment(http.Controller):

    @http.route([
        '/search/suggestion',
        '/search/suggestion/<int:city_id>'], type='http', auth="public", website=True)
    def search_suggestion(self, city_id, **post):
        cita = []
        if post:
            partner = request.env.user.partner_id
            query = post.get('query').lower()
            for suggestion in query.split(" "):
                judged_id = partner.parent_id
                if partner.appointment_type != 'scheduler':
                    suggested_appointment_types = request.env['calendar.appointment.type'].sudo().search_calendar(judged_id.id)
                else:
                    if city_id: #city selected
                        suggested_appointment_types = request.env['calendar.appointment.type'].sudo().search([('city_id','=',city_id),('name','!=',False)])
                    else:
                        suggested_appointment_types = request.env['calendar.appointment.type'].sudo().search([])
                for appointment_type in suggested_appointment_types:
                    if len(cita) > 0 and appointment_type.id in [line.get('id') for line in cita]:
                        continue
                    city = appointment_type.judged_id.city_id.name if \
                        appointment_type.judged_id and appointment_type.judged_id.city_id else '404'
                    name = city + '-' + appointment_type.name
                    cita.append({
                        'cita': name,
                        'id': appointment_type.id,
                        })
        data = {}
        data['status'] = True,
        data['error'] = None,
        data['data'] = {'cita': cita}
        return json.dumps(data)



class OdooWebsiteSearchCity(http.Controller):

    @http.route(['/search/suggestion_city'], type='http', auth="public", website=True)
    def search_suggestion(self, city_id=None, **post):
        cities = []
        if post:
            query = post.get('query').lower()
            for suggestion in query.split(" "):
                suggested_cities = request.env['res.city'].sudo().search([])
                for city in suggested_cities:
                    #if len(cities) > 0 and city.id in [line.get('id') for line in cities]:
                    #    continue
                    cities.append({
                        'city': '%s - %s' % (city.name, city.state_id.name),
                        'id': city.id,
                        })
        data = {}
        data['status'] = True,
        data['error'] = None,
        data['data'] = {'cities': cities}

        return json.dumps(data)


class OdooWebsiteSearchSolicitante(http.Controller):

    @http.route(['/search/suggestion2'], type='http', auth="public", website=True)
    def search_suggestion(self, **post):
        cita = []
        if post:
            for suggestion in post.get('query').split(" "):
                suggested_companies = request.env['res.partner'].sudo().search_company_type()
                for companie in suggested_companies:
                    city = companie.city_id.name if companie.city_id else '404'
                    name = city + '-' + companie.name
                    cita.append({
                        'cita': name,
                        'id': companie.id,
                        })
        data = {}
        data['status'] = True,
        data['error'] = None,
        data['data'] = {'cita': cita}
        return json.dumps(data)

class OdooWebsiteSearchDestino(http.Controller):

    @http.route(['/search/destino'], type='http', auth="public", website=True)
    def search_suggestion(self, **post):
        suggestion_list = []
        destino = []
        if post:
            for suggestion in post.get('query').split(" "):
                suggested_partners = request.env['res.partner'].sudo().search([('company_type','=','company')])
                read_partners = suggested_partners.read(['name', 'id', 'code'])
                suggestion_list += read_partners

        for line in suggestion_list:
            destino.append({'destino': line['name'], 'id': line['id']})
        #logger.info(destino)
        data = {}
        data['status'] = True,
        data['error'] = None,
        data['data'] = {'destino': destino}
        return json.dumps(data)
