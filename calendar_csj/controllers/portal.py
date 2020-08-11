# -*- coding: utf-8 -*-

from collections import OrderedDict
from operator import itemgetter

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem

from odoo.osv.expression import OR

import logging
_logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        values['appointment_count'] = request.env['calendar.appointment'].search_count([])
        return values

    # ------------------------------------------------------------
    # My Appointments
    # ------------------------------------------------------------
    def _appointment_get_page_view_values(self, appointment, access_token, **kwargs):
        values = {
            'page_name': 'appointment',
            'appointment': appointment,
        }
        return self._get_page_view_values(appointment, access_token, values, 'my_appointment_history', False, **kwargs)


    @http.route(['/my/appointments', '/my/appointments/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_appointments(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby='appointment', **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'create_date desc'},
            'appointment_code': {'label': _('Appointment ID'), 'order': 'appointment_code desc'},
            'state': {'label': _('State'), 'order': 'state'},
            'city': {'label': _('City'), 'order': 'name'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
            'stage': {'input': 'stage', 'label': _('Search in Stages')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'appointment': {'input': 'appointment_code', 'label': _('Appointment')},
        }

        # extends filterby criteria with project the customer has access to
        appointments = request.env['calendar.appointment'].search([])
        for appointment in appointments:
            searchbar_filters.update({
                str(appointment.id): {'label': appointment.name, 'domain': [('state', '=', 'open')]}
            })

        # extends filterby criteria with project (criteria name is the project id)
        # Note: portal users can't view projects they don't follow
        #project_groups = request.env['project.task'].read_group([('project_id', 'not in', projects.ids)],
        #                                                        ['project_id'], ['project_id'])

        #for group in appointment_groups:
        #    proj_id = group['project_id'][0] if group['project_id'] else False
        #    proj_name = group['project_id'][1] if group['project_id'] else _('Others')
        #    searchbar_filters.update({
        #        str(proj_id): {'label': proj_name, 'domain': [('project_id', '=', proj_id)]}
        #    })

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
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # appointments count
        #appointment_count = Appointment.search_count(domain)

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search)]])
            if search_in in ('stage', 'all'):
                search_domain = OR([search_domain, [('stage_id', 'ilike', search)]])
            domain += search_domain

        # task count
        appointment_count = request.env['calendar.appointment'].search_count(domain)


        # pager
        pager = portal_pager(
            url="/my/appointments",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=appointment_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        appointments = request.env['calendar.appointment'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_appointments_history'] = appointments.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'appointments': appointments,
            'page_name': 'appointment',
            'archive_groups': archive_groups,
            'default_url': '/my/appointments',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("calendar_csj.portal_my_appointments", values)

    @http.route(['/my/appointment/<int:appointment_id>'], type='http', auth="public", website=True)
    def portal_my_project(self, appointment_id=None, access_token=None, **kw):
        try:
            appointment_sudo = self._document_check_access('calendar.appointment', appointment_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._appointment_get_page_view_values(appointment_sudo, access_token, **kw)

        _logger.error("++++++++++++++++++++++++\n++++++++++++++++++++++++++++\n+++++++++++++++++++++++++")
        _logger.error(appointment_sudo)
        _logger.error(values)

        return request.render("calendar_csj.portal_my_appointment", values)



    @http.route(['/my/task/<int:task_id>'], type='http', auth="public", website=True)
    def portal_my_task(self, task_id, access_token=None, **kw):
        try:
            task_sudo = self._document_check_access('project.task', task_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # ensure attachment are accessible with access token inside template
        for attachment in task_sudo.attachment_ids:
            attachment.generate_access_token()
        values = self._task_get_page_view_values(task_sudo, access_token, **kw)
        return request.render("project.portal_my_task", values)
