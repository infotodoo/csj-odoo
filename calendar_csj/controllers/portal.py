# -*- coding: utf-8 -*-

from collections import OrderedDict
from operator import itemgetter
from odoo import http, fields, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import content_disposition, request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem
from odoo import models, fields, api
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import html2plaintext, DEFAULT_SERVER_DATETIME_FORMAT as dtf
import pytz
import io
from odoo.tools.misc import get_lang
from babel.dates import format_datetime, format_date
from werkzeug.urls import url_encode
from datetime import datetime
import xlsxwriter

from odoo.osv.expression import OR

import logging
_logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        # when partner is not scheduler they can only view their own
        partner = request.env.user.partner_id
        judged_id = partner.parent_id
        domain = []
        if partner.appointment_type != 'scheduler':
            domain += [('partner_id', '=', judged_id.id)]
        values['appointment_count'] = request.env['calendar.appointment'].search_count(domain)
        return values

    # ------------------------------------------------------------
    # My Appointments
    # ------------------------------------------------------------
    def _appointment_get_page_view_values(self, appointment, access_token, **kwargs):
        if appointment.request_type == 'A':
            suggested_class = request.env['calendar.class'].sudo().search([('type','=','audience')])
        else:
            suggested_class = request.env['calendar.class'].sudo().search([('type','=','other')])
        suggested_help1 = request.env['calendar.help'].sudo().search([('type','=','support')])
        suggested_help2 = request.env['calendar.help'].sudo().search([('type','=','type_p')])
        values = {
            'page_name': 'appointment',
            'appointment': appointment,
            'suggested_class': suggested_class,
            'suggested_help1': suggested_help1,
            'suggested_help2': suggested_help2,
            'appointment_judged_type' : request.env.user.partner_id.appointment_type
        }
        return self._get_page_view_values(appointment, access_token, values, 'my_appointment_history', False, **kwargs)


    @http.route(['/my/appointments', '/my/appointments/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_appointments(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='appointment_code', groupby='none', export='none', **kw):
        values = self._prepare_portal_layout_values()

        searchbar_sortings = {
            'date': {'label': _('Fecha de Realización'), 'order': 'calendar_datetime desc'},
            'appointment_code': {'label': _('Agendamiento ID'), 'order': 'appointment_code desc'},
            'state': {'label': _('Estado'), 'order': 'state'},
            'city_id': {'label': _('Ciudad'), 'order': 'name'},
            'country_state_id': {'label': _('Departamento'), 'order': 'name'},
            'process_number': {'label': _('Número de Proceso'), 'order': 'process_number'},
        }

        searchbar_filters = {
            'all': {'label': _('Todos'), 'domain': []},
            'today': {'label': _('Hoy'), 'domain': [('calendar_datetime','<',datetime(2020,8,12,23,59,59)),('calendar_datetime','>',datetime(2020,8,12,0,0,1))]},
            'month': {'label': _('Último Mes'), 'domain': [('calendar_datetime','>',datetime(2020,8,1,0,0,1)),('calendar_datetime','<',datetime(2020,8,31,23,59,59))]},
            'realized': {'label': _('Realizada'), 'domain': [('state','=','realized')]},
            'open': {'label': _('Agendado'), 'domain': [('state','=','open')]},
            'unrealized': {'label': _('No realizada'), 'domain': [('state','=','unrealized')]},
            'postpone': {'label': _('Aplazado'), 'domain': [('state','=','postpone')]},
            'assist_postpone': {'label': _('Asistida y aplazada'), 'domain': [('state','=','assist_postpone')]},
            'assist_cancel': {'label': _('Asistida y Cancelada'), 'domain': [('state','=','assist_cancel')]},
            'draft': {'label': _('Duplicado'), 'domain': [('state','=','draft')]},
            'cancel': {'label': _('Cancelado'), 'domain': [('state','=','cancel')]},
        }

        searchbar_inputs = {
            'appointment_code': {'input': 'appointment_code', 'label': _('Buscar <span class="nolabel"> (en Id Agendamiento)</span>')},
            'process_number': {'input': 'process_number', 'label': _('Buscar por Número de Proceso')},
            'city_id': {'input': 'city_id', 'label': _('Ciudad')},
            'create_uid': {'input': 'create_uid', 'label': _('Creado por')},
            'judged_only_name': {'input': 'judged_only_name', 'label': _('Despacho solicitante')},
            'applicant_id': {'input': 'applicant_id', 'label': _('Buscar por Nombre Solicitante')},
            'declarant_text': {'input': 'declarant_text', 'label': _('Buscar por Declarante')},
            'tag_number': {'input': 'tag_number', 'label': _('Buscar Etiqueta')},
            'indicted_text': {'input': 'indicted_text', 'label': _('Buscar por Procesado')},
            'applicant_email': {'input': 'applicant_email', 'label': _('Buscar por Email del Aplicante')},
            'lifesize_meeting_ext': {'input': 'lifesize_meeting_ext', 'label': _('Buscar por Ext reunión Lifesize')},
            'name': {'input': 'name', 'label': _('Buscar por API Lifesize')},
            'state': {'input': 'state', 'label': _('Buscar por Estado')},
            'all': {'input': 'all', 'label': _('Buscar en Todos')},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            #'appointment': {'input': 'appointment_code', 'label': _('Appointment')},
            'state': {'input': 'state', 'label': _('State')},
        }


        """appointments = request.env['calendar.appointment'].search([])
            for appointment in appointments:
                searchbar_filters.update({
                    str(appointment.id): {'label': appointment.name, 'domain': [('state', '=', 'open')]}
                })
        """

        #for appointment in appointments:
        #    searchbar_filters.update({
        #        str(appointment.id): {'label': appointment.name, 'domain': [('appointment_id', '=', appointment.id)]}
        #    })

        # extends filterby criteria with project (criteria name is the project id)
        # Note: portal users can't view projects they don't follow
        #appointment_groups = request.env['calendar.appointment'].read_group([('project_id', 'not in', projects.ids)],
        #                                                        ['project_id'], ['project_id'])
        """
        for group in appointment_groups:
            proj_id = group['project_id'][0] if group['project_id'] else False
            proj_name = group['project_id'][1] if group['project_id'] else _('Others')
            searchbar_filters.update({
                str(proj_id): {'label': proj_name, 'domain': [('project_id', '=', proj_id)]}
            })
        """
        # default sort by value
        if not sortby:
            sortby = 'appointment_code'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']


        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('calendar.appointment', domain)
        if date_begin and date_end:
            date_begin = datetime.strptime(date_begin, '%Y-%m-%d %H:%M')
            date_begin = date_begin + timedelta(hours=5)
            date_end = datetime.strptime(date_end, '%Y-%m-%d %H:%M')
            date_end = date_end + timedelta(hours=5)
            domain += [('calendar_datetime', '>=', date_begin), ('calendar_datetime', '<=', date_end)]

        # appointments count
        #appointment_count = Appointment.search_count(domain)

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('appointment_code', 'all'):
                search_domain = OR([search_domain, [('appointment_code', 'ilike', search)]])
            if search_in in ('create_uid', 'all'):
                search_domain = OR([search_domain, [('create_uid', 'ilike', search)]])
            if search_in in ('city_id', 'all'):
                search_domain = OR([search_domain, [('city_id', 'ilike', search)]])
            if search_in in ('judged_only_name', 'all'):
                search_domain = OR([search_domain, [('judged_only_name', 'ilike', search)]])
            if search_in in ('process_number', 'all'):
                search_domain = OR([search_domain, [('process_number', 'ilike', search)]])
            if search_in in ('applicant_id', 'all'):
                search_domain = OR([search_domain, [('applicant_id', 'ilike', search)]])
            if search_in in ('declarant_text', 'all'):
                search_domain = OR([search_domain, [('declarant_text', 'ilike', search)]])
            if search_in in ('tag_number', 'all'):
                search_domain = OR([search_domain, [('tag_number', 'ilike', search)]])
            if search_in in ('indicted_text', 'all'):
                search_domain = OR([search_domain, [('indicted_text', 'ilike', search)]])
            if search_in in ('applicant_email', 'all'):
                search_domain = OR([search_domain, [('applicant_email', 'ilike', search)]])
            domain += search_domain
            if search_in in ('lifesize_meeting_ext', 'all'):
                search_domain = OR([search_domain, [('lifesize_meeting_ext', 'ilike', search)]])
            domain += search_domain
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            domain += search_domain
            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain

        _logger.error(domain)

        # when partner is not scheduler they can only view their own
        partner = request.env.user.partner_id
        judged_id = partner.parent_id
        if partner.appointment_type != 'scheduler':
            domain += [('partner_id', '=', judged_id.id)]

        appointment_count = request.env['calendar.appointment'].search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/appointments",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'search': search, 'sortby': sortby, 'filterby': filterby, 'search_in': search_in},
            total=appointment_count,
            page=page,
            step=self._items_per_page
        )

        if groupby == 'state':
            order = "state, %s" % order
        appointments = request.env['calendar.appointment'].sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        if groupby == 'state':
            grouped_appointments = [request.env['calendar.appointment'].sudo().concat(*g) for k, g in groupbyelem(appointments, itemgetter('state'))]
        else:
            grouped_appointments = [appointments]

        # content according to pager and archive selected
        appointments = request.env['calendar.appointment'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_appointments_history'] = appointments.ids[:100]


        # excel generation
        # Create a workbook and add a worksheet.
        #if export == 'on' and date_begin and date_end:
        if export == 'on':
            appointments_total = request.env['calendar.appointment'].sudo().search(domain, order=order)
            response = request.make_response(
                None,
                headers=[('Content-Type', 'application/vnd.ms-excel'), ('Content-Disposition', content_disposition('Reporte_Agendamientos.xlsx'))
                ]
            )
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True, 'default_date_format': 'yyyy/mm/dd'})
            sheet = workbook.add_worksheet('Agendamientos')
            cell_format = workbook.add_format()
            head = workbook.add_format()
            txt = workbook.add_format()
            dateformat = workbook.add_format()
            timeformat = workbook.add_format()
            datetimeformat = workbook.add_format()

            sheet.set_column('A:A', 20)
            sheet.set_column('B:B', 40)
            sheet.set_column('C:C', 20)
            sheet.set_column('C:C', 20)
            sheet.set_column('D:D', 20, dateformat)
            sheet.set_column('E:E', 20)
            sheet.set_column('F:F', 20)
            sheet.set_column('G:G', 60)
            sheet.set_column('H:H', 20)
            sheet.set_column('I:I', 20)
            sheet.set_column('J:J', 20)
            sheet.set_column('K:K', 20)
            sheet.set_column('L:L', 50)
            sheet.set_column('M:M', 50)
            sheet.set_column('N:N', 20, dateformat)
            sheet.set_column('O:O', 40)
            sheet.set_column('P:P', 20)
            sheet.set_column('Q:Q', 50)
            sheet.set_column('R:R', 30)
            sheet.set_column('S:S', 20)
            sheet.set_column('T:T', 40)
            sheet.set_column('U:U', 20)
            sheet.set_column('V:V', 20)
            sheet.set_column('W:W', 20)
            sheet.set_column('X:X', 20)
            sheet.set_column('Y:Y', 40, dateformat)
            sheet.set_column('Z:Z', 20)
            sheet.set_column('AA:AA', 50)
            sheet.set_column('AB:AB', 20, dateformat)
            sheet.set_column('AC:AC', 20)
            sheet.set_column('AD:AD', 20, dateformat)
            sheet.set_column('AE:AE', 20, timeformat)
            sheet.set_column('AF:AF', 20)
            sheet.set_column('AG:AG', 20)
            sheet.set_column('AH:AH', 60)
            sheet.set_column('AI:AI', 60)
            sheet.set_column('AJ:AJ', 20)
            sheet.set_column('AK:AK', 40)
            sheet.set_column('AL:AL', 20)
            sheet.set_column('AM:AM', 40, datetimeformat)

            #sheet.merge_range('B2:I3', 'REPORTE DE AGENDAMIENTOS', head)
            sheet.write('A1', 'ID SOLICITUD', head)
            sheet.write('B1', 'TIPO DE SOLICITUD', head)
            sheet.write('C1', 'TIPO DE AUDIENCIA', head)
            sheet.write('D1', 'FECHA DE REALIZACIÓN', head)
            sheet.write('E1', 'HORA DE INICIO', head)
            sheet.write('F1', 'CÓDIGO DESPACHO SOLICITANTE', head)
            sheet.write('G1', 'DESPACHO SOLICITANTE', head)
            sheet.write('H1', 'CIUDAD ORIGEN', head)
            sheet.write('I1', 'DEPARTAMENTO ORIGEN', head)
            sheet.write('J1', 'DESTINOS', head)
            sheet.write('K1', 'MEDIO DE RECEPCIÓN', head)
            sheet.write('L1', 'DETALLES MEDIO DE RECEPCIÓN', head)
            sheet.write('M1', 'OBSERVACIONES', head)
            sheet.write('N1', 'FECHA DE SOLICITUD', head)
            sheet.write('O1', 'NOMBRE DEL SOLICITANTE', head)
            sheet.write('P1', 'ESTADO', head)
            sheet.write('Q1', 'CORREO SALIENTE', head)
            sheet.write('R1', 'NÚMERO DE PROCESO', head)
            sheet.write('S1', 'SALA', head)
            sheet.write('T1', 'CORREO PARTICIPANTES', head)
            sheet.write('U1', 'CELULAR', head)
            sheet.write('V1', 'CLASE DE VIDEOCONFERENCIA', head)
            sheet.write('W1', 'TIPO DE AUDIENCIA', head)
            #sheet.write('X1', 'DECLARANTE', head)
            #sheet.write('Y1', 'PROCESADO', head)
            sheet.write('X1', 'FECHA AGENDAMIENTO', head)
            sheet.write('Y1', 'USUARIO AGENDAMIENTO', head)
            sheet.write('Z1', 'FECHA CIERRE', head)
            sheet.write('AA1', 'USUARIO DE CIERRE', head)
            sheet.write('AB1', 'FECHA FINAL', head)
            sheet.write('AC1', 'HORA FINAL', head)
            sheet.write('AD1', 'DESCRIPCION', head)
            sheet.write('AE1', 'ETIQUETA', head)
            sheet.write('AF1', 'URL DE GRABACIÓN', head)
            sheet.write('AG1', 'DESCARGA DE GRABACIÓN', head)
            sheet.write('AH1', 'CREADO POR', head)
            sheet.write('AI1', 'NOMBRE SALA LIFESIZE', head)
            sheet.write('AJ1', 'URL LIFESIZE', head)
            sheet.write('AK1', 'FECHA Y HORA DE REALIZACIÓN', head)
            row = 2

            for appointment in appointments_total:
    ########## ##TRADUCCION ESTADOS ###################
                if appointment.state == 'open':
                    state_label='AGENDADO'
                if appointment.state == 'realized':
                    state_label='REALIZADA'
                if appointment.state == 'unrealized':
                    state_label='NO REALIZADA'
                if appointment.state == 'assist_postpone':
                    state_label='ASISTIDA Y APLAZADA'
                if appointment.state == 'postpone':
                    state_label='APLAZADA'
                if appointment.state == 'assist_cancel':
                    state_label='ASISTIDA Y CANCELADA'
                if appointment.state == 'cancel':
                    state_label='CANCELADO'
                if appointment.state == 'draft':
                    state_label='DUPLICADO'
########## ##TRADUCIÓN TIPO AUDIENCIA ###################

                if appointment.type == 'audience':
                    type_label='AUDIENCIA'
                if appointment.type == 'conference':
                    type_label='VIDEO CONFERENCIA'
                if appointment.type == 'streaming':
                    type_label='STREAMING'



                sheet.write('A'+str(row), appointment.appointment_code, cell_format)
                sheet.write('B'+str(row), appointment.request_type_label, cell_format)
                sheet.write('C'+str(row), type_label, cell_format)
                sheet.write('D'+str(row), str(appointment.calendar_date), cell_format)
                newstrtime = '{0:02.0f}:{1:02.0f}'.format(*divmod(appointment.calendar_time * 60, 60))
                sheet.write('E'+str(row), newstrtime, cell_format)
                sheet.write('F'+str(row), appointment.judged_only_code, cell_format)
                sheet.write('G'+str(row), appointment.judged_only_name, cell_format)
                sheet.write('H'+str(row), appointment.city_id.name.upper(), cell_format)
                sheet.write('I'+str(row), appointment.country_state_id.name.upper(), cell_format)
                sheet.write('J'+str(row), appointment.destination_ids_label, cell_format)
                sheet.write('K'+str(row), appointment.reception_id.name, cell_format)
                sheet.write('L'+str(row), appointment.reception_detail.upper(), cell_format)
                sheet.write('M'+str(row), appointment.observations.upper(), cell_format)
                sheet.write('N'+str(row), str(appointment.request_date), dateformat)
                sheet.write('O'+str(row), appointment.applicant_id.name.upper(), cell_format)
                sheet.write('P'+str(row), state_label, cell_format)
                sheet.write('Q'+str(row), appointment.applicant_email, cell_format)
                sheet.write('R'+str(row), appointment.process_number, cell_format)
                sheet.write('S'+str(row), appointment.room_id_mame.upper() if appointment.room_id_mame else '', cell_format)
                sheet.write('T'+str(row), appointment.partner_ids_label, cell_format)
                sheet.write('U'+str(row), appointment.applicant_mobile, cell_format)
                sheet.write('V'+str(row), appointment.class_id.name.upper(), cell_format)
                sheet.write('W'+str(row), appointment.request_type.upper(), cell_format)
                #sheet.write('X'+str(row), appointment.declarant_text.upper(), cell_format)
                #sheet.write('Y'+str(row), appointment.indicted_text.upper(), cell_format)
                sheet.write('X'+str(row), str(appointment.appointment_date), cell_format)
                sheet.write('Y'+str(row), appointment.create_uid_login, cell_format)
                sheet.write('Z'+str(row), str(appointment.appointment_close_date) if appointment.appointment_close_date else '', cell_format)
                sheet.write('AA'+str(row), appointment.appointment_close_user_login if appointment.appointment_close_user_login else '', cell_format)
                sheet.write('AB'+str(row), str(appointment.end_date) if appointment.end_date else '', cell_format)
                newstrtime_end_hour = '{0:02.0f}:{1:02.0f}'.format(*divmod(appointment.end_hour * 60, 60))
                sheet.write('AC'+str(row), str(newstrtime_end_hour) if newstrtime_end_hour else '', cell_format)
                sheet.write('AD'+str(row), appointment.state_description.upper() if appointment.state_description else '', cell_format)
                sheet.write('AE'+str(row), appointment.tag_number, cell_format)
                sheet.write('AF'+str(row), appointment.link_download if appointment.link_download else '', cell_format)
                sheet.write('AG'+str(row), appointment.link_download_text if appointment.link_download_text else '', cell_format)
                sheet.write('AH'+str(row), appointment.create_uid.login, cell_format)
                sheet.write('AI'+str(row), appointment.name, cell_format)
                sheet.write('AJ'+str(row), appointment.lifesize_url, cell_format)
                sheet.write('AK'+str(row), str(appointment.calendar_datetime - relativedelta(hours=5)), cell_format)

                row+=1

            workbook.close()
            output.seek(0)
            response.stream.write(output.read())
            output.close()

            #response.set_cookie('fileToken', token)
            return response

        values.update({
            'date_begin': date_begin,
            'date_end': date_end,
            'appointments': appointments,
            'grouped_appointments': grouped_appointments,
            'total': appointment_count,
            'page_name': 'appointment',
            'archive_groups': archive_groups,
            'default_url': '/my/appointments',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'search': search,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("calendar_csj.portal_my_appointments", values)


    @http.route([
        '/my/appointment/<int:appointment_id>'
    ], type='http', auth="user", website=True)
    def portal_my_appointment(self, appointment_id=None, access_token=None, **kw):
        try:
            #appointment_sudo = self._document_check_access('calendar.appointment', appointment_id, access_token)
            # Don't work with _document_check_access for compute tag_number field
            appointment_sudo = request.env['calendar.appointment'].sudo().browse(appointment_id)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._appointment_get_page_view_values(appointment_sudo, access_token, **kw)
        return request.render("calendar_csj.portal_my_appointment", values)


    @http.route(['/my/appointment/<model("calendar.appointment"):appointment_id>/update/state/cancel'], type='http', auth="user", website=True)
    def portal_my_appointment_cancel(self, appointment_id=None, access_token=None, **kw):
        appointment_id.action_cancel()
        return request.redirect('/my/appointment/' + str(appointment_id.id))

    @http.route(['/my/appointment/<model("calendar.appointment"):appointment_id>/update/state/realized'], type='http', auth="user", website=True)
    def portal_my_appointment_realized(self, appointment_id=None, access_token=None, **kw):
        appointment_id.write({
            'state' : 'realized',
            'appointment_close_date': datetime.now(),
            'appointment_close_user_id': request.env.user.id,
        });
        return request.redirect('/my/appointment/' + str(appointment_id.id))

    @http.route(['/my/appointment/<model("calendar.appointment"):appointment_id>/update/state/unrealized'], type='http', auth="user", website=True)
    def portal_my_appointment_unrealized(self, appointment_id=None, access_token=None, **kw):
        appointment_id.write({
            'state' : 'unrealized',
            'appointment_close_date': datetime.now(),
            'appointment_close_user_id': request.env.user.id,
        });
        return request.redirect('/my/appointment/' + str(appointment_id.id))

    @http.route(['/my/appointment/<model("calendar.appointment"):appointment_id>/update/state/postpone'], type='http', auth="user", website=True)
    def portal_my_appointment_postpone(self, appointment_id=None, access_token=None, **kw):
        appointment_id.write({
            'state' : 'postpone',
            'appointment_close_date': datetime.now(),
            'appointment_close_user_id': request.env.user.id,
        });
        return request.redirect('/my/appointment/' + str(appointment_id.id))

    @http.route(['/my/appointment/<model("calendar.appointment"):appointment_id>/update/state/assist_postpone'], type='http', auth="user", website=True)
    def portal_my_appointment_assist_postpone(self, appointment_id=None, access_token=None, **kw):
        appointment_id.write({
            'state' : 'assist_postpone',
            'appointment_close_date': datetime.now(),
            'appointment_close_user_id': request.env.user.id,
        });
        return request.redirect('/my/appointment/' + str(appointment_id.id))

    @http.route(['/my/appointment/<model("calendar.appointment"):appointment_id>/update/state/assist_cancel'], type='http', auth="user", website=True)
    def portal_my_appointment_assist_cancel(self, appointment_id=None, access_token=None, **kw):
        appointment_id.write({
            'state' : 'assist_cancel',
            'appointment_close_date': datetime.now(),
            'appointment_close_user_id': request.env.user.id,
        });
        return request.redirect('/my/appointment/' + str(appointment_id.id))
    
    @http.route(['/my/appointment/<model("calendar.appointment"):appointment_id>/update/state/open'], type='http', auth="user", website=True)
    def portal_my_appointment_assist_open(self, appointment_id=None, access_token=None, **kw):
        appointment_id.write({
            'state' : 'open',
            'appointment_close_date': datetime.now(),
            'appointment_close_user_id': request.env.user.id,
        });
        return request.redirect('/my/appointment/' + str(appointment_id.id))
    
    @http.route(['/my/appointment/<model("calendar.appointment"):appointment_id>/update/state/draft'], type='http', auth="user", website=True)
    def portal_my_appointment_assist_draft(self, appointment_id=None, access_token=None, **kw):
        appointment_id.write({
            'state' : 'draft',
            'appointment_close_date': datetime.now(),
            'appointment_close_user_id': request.env.user.id,
        });
        return request.redirect('/my/appointment/' + str(appointment_id.id))


    @http.route(['/my/appointment/<int:appointment_id>/update/all'], type='http', auth="user", website=True)
    def portal_my_appointment_edit(self, appointment_id=None, access_token=None, **kw):
        try:
            appointment_sudo = self._document_check_access('calendar.appointment', appointment_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._appointment_get_page_view_values(appointment_sudo, access_token, **kw)
        return request.render("calendar_csj.portal_my_appointment_editall", values)


    @http.route(['/my/appointment/<model("calendar.appointment"):appointment_id>/update/all/submit'], type='http', auth="public", website=True, method=["POST"])
    def appointment_portal_edit_form_submit(self, **kwargs):
        kwargs['appointment_id'].sudo().write({
            'end_date': kwargs['end_date'] if 'end_date' in kwargs else '',
            'end_hour': float(kwargs['end_hour'].replace(":","."))  if 'end_hour' in kwargs else '',
            'link_download': kwargs['link_download'] if 'link_download' in kwargs else '',
            'link_streaming': kwargs['link_streaming'] if 'link_streaming' in kwargs else '',
            'state_description': kwargs['state_description'] if 'state_description' in kwargs else '',
            'observations': kwargs['observations'],
        })
        return request.redirect('/my/appointment/' + str(kwargs['appointment_id'].id))


    @http.route([
        '/my/appointment/<int:appointment_id>/update/reschedule'
    ], type='http', auth="user", website=True)
    def portal_my_appointment_reschedule(self, appointment_id=None, access_token=None, **kw):
        try:
            appointment_sudo = self._document_check_access('calendar.appointment', appointment_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._appointment_get_page_view_values(appointment_sudo, access_token, **kw)
        return request.render("calendar_csj.portal_my_appointment_reschedule", values)




    @http.route(['/my/appointment/<model("calendar.appointment"):appointment_id>/update/reschedule/submit'], type='http', auth="public", website=True, method=["POST"])
    def appointment_portal_reschedule_form_submit(self, calendar_datetime, calendar_duration, appointment_type, **kwargs):
        request.session['timezone'] = 'America/Bogota'
        day_name = format_datetime(datetime.strptime(calendar_datetime, "%Y-%m-%d %H:%M"), 'EEE', locale=get_lang(request.env).code)
        date_formated = format_datetime(datetime.strptime(calendar_datetime, "%Y-%m-%d %H:%M"), locale=get_lang(request.env).code)
        timezone = request.session['timezone']
        tz_session = pytz.timezone(timezone)
        date_start = tz_session.localize(fields.Datetime.from_string(calendar_datetime)).astimezone(pytz.utc)
        date_end = date_start + relativedelta(hours=float(calendar_duration))

        appointment_type_obj = request.env['calendar.appointment.type'].browse(appointment_type)

        new_date = date_start.strftime(dtf)
        if str(date_start.strftime(dtf)) == str(kwargs['appointment_id'].calendar_datetime):
            new_date = None

        kwargs['appointment_id'].sudo().write({
            'calendar_datetime': new_date,
        })

        return request.redirect('/my/appointment/' + str(kwargs['appointment_id'].id))


    @http.route([
        '/my/appointment/<int:appointment_id>/update/judged'
    ], type='http', auth="user", website=True)
    def portal_my_appointment_judged(self, appointment_id=None, access_token=None, **kw):
        try:
            appointment_sudo = self._document_check_access('calendar.appointment', appointment_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._appointment_get_page_view_values(appointment_sudo, access_token, **kw)
        return request.render("calendar_csj.portal_my_appointment_judged_change", values)


    @http.route(['/my/appointment/<model("calendar.appointment"):appointment_id>/update/judged/submit'], type='http', auth="public", website=True, method=["POST"])
    def appointment_portal_judgededit_form_submit(self, appointment_id=None, **kwargs):
        appointment_type_obj = request.env['calendar.appointment.type'].search([ ('id','=',kwargs['appointment_type']) ])

        appointment_obj = request.env['calendar.appointment'].browse(appointment_id.id)
        appointment_obj.write({
            'appointment_type_id': appointment_type_obj.id,
        })
        judged_extension_lifesize = False
        partner = appointment_obj.appointment_type_id.judged_id if appointment_obj \
            and appointment_obj.appointment_type_id.judged_id else False
        if partner and partner.extension_lifesize:
            judged_extension_lifesize = partner.extension_lifesize

        description = ("Updated to: %s " % (
            appointment_obj.calendar_datetime.strftime("%Y%m%d %H%M%S"))
            )
        api = {
            'method': 'update',
            'uuid': appointment_obj.lifesize_uuid,
            'description': description,
            'ownerExtension': judged_extension_lifesize or \
                request.env.user.company_id.owner_extension,
            'moderatorExtension': judged_extension_lifesize or \
                request.env.user.company_id.owner_extension,
        }

        resp = request.env['api.lifesize'].api_crud(api)
        dic = request.env['api.lifesize'].resp2dict(resp)

        return request.redirect('/my/appointment/' + str(appointment_id.id))

    
    @http.route([
        '/private/videos'
    ], type='http', auth="user", website=True)
    #def portal_my_videos(self, appointment_id=None, access_token=None, **kw):
    def portal_my_videos(self, appointment_id=None, access_token=None, **kw):
        _logger.error(request.httprequest.cookies.get('session_id'))
        sid = request.httprequest.cookies.get('session_id')
        uid = request.env.user.id
        #_logger.error(request.httprequest.cookies.get())
        #_logger.error(request.csrf_token())
        #qcontext = request.session()
        if not sid:
            raise werkzeug.exceptions.NotFound()
        values = {
            'url_calltech': 'https://apigestionaudiencias3.ramajudicial.gov.co/' + str(sid) + '/' + str(uid),
        }
        return request.render("calendar_csj.portal_my_videos", values)
    
    
    @http.route([
        '/public/videos'
    ], type='http', auth="public", website=True)
    #def portal_my_videos(self, appointment_id=None, access_token=None, **kw):
    def portal_public_videos(self, appointment_id=None, access_token=None, **kw):
        _logger.error(request.httprequest.cookies.get('session_id'))
        sid = request.httprequest.cookies.get('session_id')
        uid = request.env.user.id
        #_logger.error(request.httprequest.cookies.get())
        #_logger.error(request.csrf_token())
        #qcontext = request.session()
        if not sid:
            raise werkzeug.exceptions.NotFound()
        values = {
            #'url_calltech': 'https://streamcuc.web.app/public',
            'url_calltech': 'https://apigestionaudiencias3.ramajudicial.gov.co/public',
        }
        return request.render("calendar_csj.portal_public_videos", values)