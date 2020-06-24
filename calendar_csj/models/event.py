# -*- coding: utf-8 -*-
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
import logging
_logger = logging.getLogger(__name__)



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

            #event.add('method').value = 'REQUEST'
            event.add('created').value = ics_datetime(fields.Datetime.now())
            event.add('dtstart').value = ics_datetime(meeting.start, meeting.allday)
            event.add('dtend').value = ics_datetime(meeting.stop, meeting.allday)
            event.add('summary').value = meeting.name
            event.add('class').value = 'PUBLIC'
            event.add('trans').value = 'OPAQUE'
            event.add('location').value = 'COLOMBIA'
            if self.state == 'cancel':
                event.add('status').value = 'CANCEL'
            else:
                event.add('status').value = 'CONFIRMED'
            event.add('uid').value = self.appointment_id.process_number
            event.add('sequence').value = str(self.appointment_id.sequence)
            if meeting.description:
                event.add('description').value = meeting.description
            if meeting.location:
                event.add('location').value = meeting.location
            if meeting.rrule:
                event.add('rrule').value = meeting.rrule

            organizer_add = event.add('organizer')
            organizer_add.params['CN'] = ["agendamiento.csj@gmail.com"]
            organizer_add.value = "agendamiento.csj@gmail.com"

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
                attendee_add.params['PARTSTAT'] = ["NEEDS-ACTION"]
                attendee_add.params['RSVP'] = ["TRUE"]
                attendee_add.params['CN'] = [attendee.email]
                attendee_add.params['X-NUM-GUESTS'] = ["0"]
                attendee_add.value = (attendee.email or u'')

            result[meeting.id] = cal.serialize().encode('utf-8')

        return result


    def action_sendmail(self):
        email = self.env.user.email
        if email:
            for meeting in self:
                meeting.attendee_ids._send_mail_to_attendees('calendar.calendar_template_meeting_invitation', force_send=True)
        return True
