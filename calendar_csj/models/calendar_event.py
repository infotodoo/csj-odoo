# -*- coding: utf-8 -*-
import pytz

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

def is_calendar_id(record_id):
    return len(str(record_id).split('-')) != 1

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    state = fields.Selection(selection_add=[('cancel', 'Canceled')])
    appointment_id = fields.Many2one('calendar.appointment', 'Appointment', ondelete='cascade')
    type = fields.Selection([
        ('audience', 'Audience'),
        ('conference', 'Video conference'),
        ('streaming', 'Streaming')], 'Request type', default='audience')
    applicant_id = fields.Many2one('res.partner', 'Applicant', ondelete='set null')
    declarant_id = fields.Many2one('res.partner', 'Declarant', ondelete='set null')
    declarant_text = fields.Text('Declarant input')
    indicted_id = fields.Many2one('res.partner', 'Indicted', ondelete='set null')
    indicted_text = fields.Text('Indicted input')
    destination_id = fields.Many2one('res.partner', 'Destination', ondelete='set null')
    class_id = fields.Many2one('calendar.class', 'Calendar class', ondelete='set null')
    help_id = fields.Many2one('calendar.help', 'Calendar help', ondelete='set null')
    partaker_type = fields.Many2one('calendar.help', 'Portaker Type', ondelete='set null')
    connection_type = fields.Many2one('calendar.help', 'Connection Type', ondelete='set null')
    request_type = fields.Selection([('l', 'Free'), ('r', 'Reserved')], 'Request type', default='r')
    request_date = fields.Char('Request Date')
    process_number = fields.Char('Process number')
    appointment_code = fields.Char('Appointment Code', related='appointment_id.appointment_code', store=True)
    reception_id = fields.Many2one('calendar.reception', 'Reception medium', ondelete='set null')
    reception_detail = fields.Char('Reception Detail')
    destination_ids = fields.Many2many('res.partner', 'calendar_event_res_partner_destination_rel', string='Destinations', states={'done': [('readonly', True)]})


    def fetch_calendar_verify_availability(self, date_time, search_appointment):
        date_time = date_time
        return date_time

    @api.model
    def create(self, vals):
        vals.update(self.create_appointment(vals))
        vals.pop('types', None)
        vals.pop('room_id', None)
        vals.pop('applicant_raw_name', None)
        vals.pop('platform')
        vals.pop('platform_type')
        vals.pop('coorganizer')
        res = super(CalendarEvent, self).create(vals)
        res.appointment_id.write({'event_id': res.id})
        return res

    def unlink(self):
        # vals = {'state': 'cancel'}
        # self.cancel_calendar_event(vals)
        return super(CalendarEvent, self).unlink()

    def create_appointment(self, vals):
        dic = {}
        # appointment_type = self.env['calendar.appointment.type'].sudo().browse(vals.get('appointment_type_id'))
        # room_id = appointment_type.judged_id.rooms_id[0].id if appointment_type.judged_id.rooms_id else False
        if vals.get('types'):
            if vals.get('types')[0] == 'V':
                types = 'conference'
            elif vals.get('types')[0] == 'A':
                types = 'audience'
            else:
                types = 'streaming'
        else:
            types = False

        appointment = self.env['calendar.appointment'].sudo().create({
            'state': vals.get('state'),
            'calendar_datetime': vals.get('start_datetime'),
            'calendar_duration': vals.get('duration'),
            'observations': vals.get('description'),
            'partners_ids': vals.get('partner_ids'),
            'destination_ids': vals.get('destination_ids'),
            'appointment_type_id': vals.get('appointment_type_id'),
            'class_id' : vals.get('class_id'),
            'help_id': vals.get('help_id'),
            'reception_id' : vals.get('reception_id'),
            'indicted_text' : vals.get('indicted_text'),
            'declarant_text' : vals.get('declarant_text'),
            'applicant_id' : vals.get('applicant_id'),
            'process_number' : vals.get('process_number'),
            'room_id': vals.get('room_id'),
            'type': types,
            'request_type' : vals.get('request_type'),
            'request_date' : vals.get('request_date'),
            'reception_detail' : vals.get('reception_detail'),
            'partaker_type': vals.get('partaker_type'),
            'connection_type': vals.get('connection_type'),
            'applicant_raw_name': vals.get('applicant_raw_name'),
            'platform': vals.get('platform'),
            'coorganizer': vals.get('coorganizer'),
        })
        dic.update(appointment_id=appointment.id)
        return dic

    def write_appointment(self, vals):
        flag = vals.get('cw_bool') or False
        if vals.get('start_datetime') and not flag:
            for record in self:
                if record.appointment_id:
                    dic = {
                        'calendar_datetime': vals.get('start_datetime'),
                        'cw_bool': True,
                    }
                    record.appointment_id.write(dic)
            record.appointment_id.write(dic)

    def cancel_calendar_event(self):
        for record in self:
            attendee_to_email = record.attendee_ids
            if attendee_to_email:
                if record.appointment_id.teams_ok:
                    attendee_to_email._send_mail_to_attendees('calendar_csj.calendar_csj_template_meeting_teams_cancel')
                else:
                    attendee_to_email._send_mail_to_attendees('calendar_csj.calendar_csj_template_meeting_cancel')

    def create_attendees(self):
        current_user = self.env.user
        result = {}
        for meeting in self:
            alreay_meeting_partners = meeting.attendee_ids.mapped('partner_id')
            meeting_attendees = self.env['calendar.attendee']
            meeting_partners = self.env['res.partner']
            for partner in meeting.partner_ids.filtered(lambda partner: partner not in alreay_meeting_partners):
                values = {
                    'partner_id': partner.id,
                    'email': partner.email,
                    'event_id': meeting.id,
                }

                if self._context.get('google_internal_event_id', False):
                    values['google_internal_event_id'] = self._context.get('google_internal_event_id')

                # current user don't have to accept his own meeting
                #if partner == self.env.user.partner_id:
                #    values['state'] = 'accepted'

                attendee = self.env['calendar.attendee'].create(values)

                meeting_attendees |= attendee
                meeting_partners |= partner

            for partner in meeting.destination_ids.filtered(lambda partner: partner not in alreay_meeting_partners):
                values = {
                    'partner_id': partner.id,
                    'email': partner.email,
                    'event_id': meeting.id,
                }
                attendee = self.env['calendar.attendee'].create(values)

                meeting_attendees |= attendee
                meeting_partners |= partner

            if meeting_attendees and not self._context.get('detaching'):
                to_notify = meeting_attendees.filtered(lambda a: a.email != current_user.email)
                if meeting.appointment_id.teams_ok:
                    to_notify._send_mail_to_attendees('calendar_csj.calendar_template_meeting_invitation')
                else:
                    to_notify._send_mail_to_attendees('calendar.calendar_template_meeting_invitation')

            if meeting_attendees:
                meeting.write({'attendee_ids': [(4, meeting_attendee.id) for meeting_attendee in meeting_attendees]})

            if meeting_partners:
                meeting.message_subscribe(partner_ids=meeting_partners.ids)

            # We remove old attendees who are not in partner_ids now.
            all_partners = meeting.partner_ids
            all_partner_attendees = meeting.attendee_ids.mapped('partner_id')
            old_attendees = meeting.attendee_ids
            partners_to_remove = all_partner_attendees + meeting_partners - all_partners

            attendees_to_remove = self.env["calendar.attendee"]
            if partners_to_remove:
                attendees_to_remove = self.env["calendar.attendee"].search([('partner_id', 'in', partners_to_remove.ids), ('event_id', '=', meeting.id)])
                attendees_to_remove.unlink()

            result[meeting.id] = {
                'new_attendees': meeting_attendees,
                'old_attendees': old_attendees,
                'removed_attendees': attendees_to_remove,
                'removed_partners': partners_to_remove
            }
        return result


class Meeting(models.Model):
    _name = 'calendar.meeting'

    def write(self, values):
        # FIXME: neverending recurring events
        if 'rrule' in values:
            values['rrule'] = self._fix_rrule(values)

        # compute duration, only if start and stop are modified
        if not 'duration' in values and 'start' in values and 'stop' in values:
            values['duration'] = self._get_duration(values['start'], values['stop'])

        self._sync_activities(values)

        # process events one by one
        for meeting in self:
            # special write of complex IDS
            real_ids = []
            new_ids = []
            if not is_calendar_id(meeting.id):
                real_ids = [int(meeting.id)]
            else:
                real_event_id = calendar_id2real_id(meeting.id)

                # if we are setting the recurrency flag to False or if we are only changing fields that
                # should be only updated on the real ID and not on the virtual (like message_follower_ids):
                # then set real ids to be updated.
                blacklisted = any(key in values for key in ('start', 'stop', 'active'))
                if not values.get('recurrency', True) or not blacklisted:
                    real_ids = [real_event_id]
                else:
                    data = meeting.read(['start', 'stop', 'rrule', 'duration'])[0]
                    if data.get('rrule'):
                        new_ids = meeting.with_context(dont_notify=True).detach_recurring_event(values).ids  # to prevent multiple _notify_next_alarm

            new_meetings = self.browse(new_ids)
            real_meetings = self.browse(real_ids)
            all_meetings = real_meetings + new_meetings
            super(Meeting, real_meetings).write(values)

            # set end_date for calendar searching
            if any(field in values for field in ['recurrency', 'end_type', 'count', 'rrule_type', 'start', 'stop']):
                for real_meeting in real_meetings:
                    if real_meeting.recurrency and real_meeting.end_type == u'count':
                        final_date = real_meeting._get_recurrency_end_date()
                        super(Meeting, real_meeting).write({'final_date': final_date})

            attendees_create = False
            if values.get('partner_ids', False):
                attendees_create = all_meetings.with_context(dont_notify=True).create_attendees()  # to prevent multiple _notify_next_alarm

            # Notify attendees if there is an alarm on the modified event, or if there was an alarm
            # that has just been removed, as it might have changed their next event notification
            if not self._context.get('dont_notify'):
                if len(meeting.alarm_ids) > 0 or values.get('alarm_ids'):
                    partners_to_notify = meeting.partner_ids.ids
                    event_attendees_changes = attendees_create and real_ids and attendees_create[real_ids[0]]
                    if event_attendees_changes:
                        partners_to_notify.extend(event_attendees_changes['removed_partners'].ids)
                    self.env['calendar.alarm_manager']._notify_next_alarm(partners_to_notify)

            if (values.get('start_date') or values.get('start_datetime') or
                    (values.get('start') and self.env.context.get('from_ui'))) and values.get('active', True):
                for current_meeting in all_meetings:
                    if attendees_create:
                        attendees_create = attendees_create[current_meeting.id]
                        attendee_to_email = attendees_create['old_attendees'] - attendees_create['removed_attendees']
                    else:
                        attendee_to_email = current_meeting.attendee_ids

                    if attendee_to_email:
                        if meeting.appointment_id.teams_ok:
                            attendee_to_email._send_mail_to_attendees('calendar.calendar_template_meeting_teams_changedate')
                        else:
                            attendee_to_email._send_mail_to_attendees('calendar.calendar_template_meeting_changedate')
        return True