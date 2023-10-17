# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64

import babel.dates
import collections
import datetime
from datetime import timedelta, MAXYEAR
from dateutil import rrule
from dateutil.relativedelta import relativedelta
import logging
from operator import itemgetter
import pytz
import re
import time
import uuid

from odoo import api, fields, models
from odoo import tools
from odoo.addons.base.models.res_partner import _tz_get
from odoo.osv import expression
from odoo.tools.translate import _
from odoo.tools.misc import get_lang
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger(__name__)


VIRTUALID_DATETIME_FORMAT = "%Y%m%d%H%M%S"


def calendar_id2real_id(calendar_id=None, with_date=False):
    """ Convert a "virtual/recurring event id" (type string) into a real event id (type int).
        E.g. virtual/recurring event id is 4-20091201100000, so it will return 4.
        :param calendar_id: id of calendar
        :param with_date: if a value is passed to this param it will return dates based on value of withdate + calendar_id
        :return: real event id
    """
    if calendar_id and isinstance(calendar_id, str):
        res = [bit for bit in calendar_id.split('-') if bit]
        if len(res) == 2:
            real_id = res[0]
            if with_date:
                real_date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT, time.strptime(res[1], VIRTUALID_DATETIME_FORMAT))
                start = datetime.datetime.strptime(real_date, DEFAULT_SERVER_DATETIME_FORMAT)
                end = start + timedelta(hours=with_date)
                return (int(real_id), real_date, end.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
            return int(real_id)
    return calendar_id and int(calendar_id) or calendar_id


def get_real_ids(ids):
    if isinstance(ids, (str, int)):
        return calendar_id2real_id(ids)

    if isinstance(ids, (list, tuple)):
        return [calendar_id2real_id(_id) for _id in ids]


def real_id2calendar_id(record_id, date):
    return '%s-%s' % (record_id, date.strftime(VIRTUALID_DATETIME_FORMAT))

def any_id2key(record_id):
    """ Creates a (real_id: int, thing: str) pair which allows ordering mixed
    collections of real and virtual events.

    The first item of the pair is the event's real id, the second one is
    either an empty string (for real events) or the datestring (for virtual
    ones)

    :param record_id:
    :type record_id: int | str
    :rtype: (int, str)
    """
    if isinstance(record_id, int):
        return record_id, u''

    (real_id, virtual_id) = record_id.split('-')
    return int(real_id), virtual_id

def is_calendar_id(record_id):
    return len(str(record_id).split('-')) != 1


SORT_ALIASES = {
    'start': 'sort_start',
    'start_date': 'sort_start',
    'start_datetime': 'sort_start',
}
def sort_remap(f):
    return SORT_ALIASES.get(f, f)



class Meeting(models.Model):
    _inherit = 'calendar.event'


    def _get_ics_file(self):
        """ Returns iCalendar file for the event invitation.
            :returns a dict of .ics file content for each meeting
        """
        result = {}
        def ics_datetime(idate, allday=False):
            if idate:
                if allday:
                    return idate
                else:
                    return idate.replace(tzinfo=pytz.timezone('UTC'))
            return False

        try:
            # FIXME: why isn't this in CalDAV?
            import vobject
        except ImportError:
            _logger.warning("The `vobject` Python module is not installed, so iCal file generation is unavailable. Please install the `vobject` Python module")
            return result

        for meeting in self:
            cal = vobject.iCalendar()
            cal.add('method').value = 'REQUEST'
            cal.add('calscale').value = 'GREGORIAN'
            event = cal.add('vevent')
            if not meeting.start or not meeting.stop:
                raise UserError(_("First you have to specify the date of the invitation."))

            event.add('created').value = ics_datetime(fields.Datetime.now())
            event.add('dtstart').value = ics_datetime(meeting.start, meeting.allday)
            event.add('dtend').value = ics_datetime(meeting.stop, meeting.allday)
            event.add('summary').value = meeting.name
            event.add('class').value = 'PUBLIC'
            event.add('trans').value = 'OPAQUE'
            event.add('location').value = 'COLOMBIA'

            #event already cancel state
            if self.state == 'cancel':
                event.add('status').value = 'CANCELLED'
            else:
                event.add('status').value = 'CONFIRMED'
            #event.add('uid').value = self.appointment_id.process_number + datetime.datetime.now().strftime("%Y%m%Y/%H:%M:%S")
            event.add('uid').value = self.appointment_id.process_number + self.appointment_id.calendar_datetime.strftime("%Y%m%d %H%M%S")
            
            event.add('sequence').value = str(self.appointment_id.sequence_icsfile_ctl)
            if meeting.description:
                event.add('description').value = meeting.description
            #if meeting.location:
            #    event.add('location').value = meeting.location
            if meeting.rrule:
                event.add('rrule').value = meeting.rrule

            organizer_add = event.add('organizer')
            cn_value = "csj@agendamiento.co"
            """
            for server_id in self.env['ir.mail_server'].search([]):
                for user_id in server_id.user_ids:
                    if self.env.uid == user_id.id:
                        cn_value = server_id.smtp_user
            """

            organizer_add.params['CN'] = ["sistemaaudiencias.ramajudicial.gov.co"]
            organizer_add.params['ROLE'] = ["CHAIR"]
            organizer_add.params['RSVP'] = ["TRUE"]
            organizer_add.value = cn_value

            if meeting.alarm_ids:
                for alarm in meeting.alarm_ids:
                    valarm = event.add('valarm')
                    interval = alarm.interval
                    duration = alarm.duration
                    trigger = valarm.add('TRIGGER')
                    trigger.params['related'] = ["START"]
                    if interval == 'days':
                        delta = timedelta(days=duration)
                    elif interval == 'hours':
                        delta = timedelta(hours=duration)
                    elif interval == 'minutes':
                        delta = timedelta(minutes=duration)
                    trigger.value = delta
                    valarm.add('DESCRIPTION').value = alarm.name or u'Odoo'
            for attendee in meeting.attendee_ids:
                attendee_add = event.add('attendee')
                attendee_add.params['CUTYPE'] = ["INDIVIDUAL"]
                attendee_add.params['ROLE'] = ["REQ-PARTICIPANT"]
                attendee_add.params['PARTSTAT'] = ["ACCEPTED"]
                #attendee_add.params['PARTSTAT'] = ["NEEDS-ACTION"]
                attendee_add.params['RSVP'] = ["TRUE"]
                attendee_add.params['CN'] = [attendee.email]
                attendee_add.params['X-NUM-GUESTS'] = ["0"]
                attendee_add.value = (attendee.email or u'')

            result[meeting.id] = cal.serialize().encode('utf-8')

        return result


class Attendee(models.Model):
    _inherit = 'calendar.attendee'

    def _send_mail_to_attendees(self, template_xmlid, force_send=False, force_event_id=None):
        """ Send mail for event invitation to event attendees.
            :param template_xmlid: xml id of the email template to use to send the invitation
            :param force_send: if set to True, the mail(s) will be sent immediately (instead of the next queue processing)
        """
        res = False

        if self.env['ir.config_parameter'].sudo().get_param('calendar.block_mail') or self._context.get("no_mail_to_attendees"):
            return res

        calendar_view = self.env.ref('calendar.view_calendar_event_calendar')
        invitation_template = self.env.ref(template_xmlid)


        # get ics file for all meetings
        ics_files = force_event_id._get_ics_file() if force_event_id else self.mapped('event_id')._get_ics_file()

        # prepare rendering context for mail template
        colors = {
            'needsAction': 'grey',
            'accepted': 'green',
            'tentative': '#FFFF00',
            'declined': 'red'
        }
        rendering_context = dict(self._context)
        rendering_context.update({
            'color': colors,
            'action_id': self.env['ir.actions.act_window'].search([('view_id', '=', calendar_view.id)], limit=1).id,
            'dbname': self._cr.dbname,
            'base_url': self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='http://localhost:8069'),
            'force_event_id': force_event_id,
        })
        invitation_template = invitation_template.with_context(rendering_context)

        # send email with attachments
        mail_ids = []
        for attendee in self:
            if attendee.email or attendee.partner_id.email:
                # FIXME: is ics_file text or bytes?
                event_id = force_event_id.id if force_event_id else attendee.event_id.id
                ics_file = ics_files.get(event_id)

                email_values = {
                    'model': None,  # We don't want to have the mail in the tchatter while in queue!
                    'res_id': None,
                }
                if ics_file:
                    email_values['attachment_ids'] = [
                        (0, 0, {'name': 'invitation.ics',
                                'mimetype': 'text/calendar; method=REQUEST; charset=UTF-8',
                                'datas': base64.b64encode(ics_file)})
                    ]
                    mail_ids.append(invitation_template.with_context(no_document=True).send_mail(attendee.id, email_values=email_values, notif_layout='mail.mail_notification_light'))
                else:
                    mail_ids.append(invitation_template.send_mail(attendee.id, email_values=email_values, notif_layout='mail.mail_notification_light'))


        if force_send and mail_ids:
            res = self.env['mail.mail'].browse(mail_ids).send()

        return res
