# Part of Odoo, Aktiv Software.
# See LICENSE file for full copyright & licensing details.
import logging
from datetime import datetime, timedelta
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class TeamsCalendarEvent(models.Model):
    """Generate Microsoft Teams Link, Update Teams event and delete event.
    New Access token generate if it is Expired.
    """
    _inherit = "calendar.event"

    teams_link_check = fields.Boolean(string="Generate Microsoft Teams Link",
                                      tracking=True)
    teams_eventid = fields.Char()
    warning_check = fields.Boolean(default=False)

    @api.onchange('teams_link_check')
    def _check_teams_bool(self):
        """Trigger 'worning_check' boolean if user
        tries to turn off meeting link boolean.
        """
        if self.create_uid and self.videocall_location:
            if not self.teams_link_check:
                self.warning_check = True
            elif self.teams_link_check:
                self.warning_check = False

    @api.model_create_multi
    def create(self, values):
        """Call Function to generate Teams Meeting link with appropriate
        Time format and time zone if 'teams_link_check' is True.
        """
        for vals in values:
            if all([vals.get('teams_link_check'), vals.get('recurrency')]):
                raise UserError("Microsoft Teams Event can't \
                    create with Recurring Events..!")
            elif vals.get('teams_link_check') and not vals.get('recurrency'):
                if not active_user.is_authenticated:
                    raise ValidationError("Generate an access token to create a Microsoft Teams meeting.")

                attendee = self.prepare_attendee_vals(vals.get('partner_ids'))
                vals['start'] = str(vals['start'])
                vals['stop'] = str(vals['stop'])
                if vals.get('allday'):
                    start_time = datetime.strptime(
                        vals['start_date'], '%Y-%m-%d') if \
                            'start_date' in vals.keys() else self.start_date
                    end_time = datetime.strptime(
                        vals['stop_date'], '%Y-%m-%d') if \
                            'stop_date' in vals.keys() else self.stop_date
                    vals['start'] = str(start_time)
                    vals['stop'] = str(end_time + timedelta(days=1))
                else:
                    start_time = vals['start']
                    end_time = vals['stop']
                meeting_link = self.generate_meeting(vals, attendee, active_user)
                vals['start'] = start_time
                vals['stop'] = end_time
                vals['videocall_location'] = meeting_link.get('meeting_url')
                vals['teams_eventid'] = meeting_link.get('meeting_id')
                vals['description'] = meeting_link.get('meeting_body')

        return super(TeamsCalendarEvent, self).create(values)

    def write(self, values):
        """Generate a team meeting link by enabling the 'teams_meeting_check'
        boolean, update the event if it is already enabled and
        delete the event by disabling the 'teams_meeting_check' boolean.
        """
        active_user = self.env.user
        for record in self:
            attendees = []
            is_meeting = any([record.teams_link_check, values.get(
                'teams_link_check')])
            event_recurrency = any([record.recurrency, values.get('recurrency')])
            if all([is_meeting, event_recurrency]):
                raise UserError("Microsoft Teams Event can't create with Recurring Events..!")
            elif values.get('teams_link_check') and not record.videocall_location:
                if not active_user.is_authenticated:
                    raise ValidationError("Generate an access token to create a Microsoft Teams meeting.")
                for partner in record.partner_ids:
                    attendees.append({
                        "emailAddress":
                        {
                            "address": partner.email,
                            "name": partner.name
                            },
                        "type": "required"
                        })
                for vals in record.read([]):
                    if any([values.get('allday'), record.allday]):
                        end_time = datetime.strptime(values.get(
                            'stop_date'), '%Y-%m-%d') if 'stop_date' \
                                in values.keys() else datetime.strptime(
                                    str(vals['stop_date']), '%Y-%m-%d')
                        vals['start'] = values.get('start_date') if \
                            'start_date' in values.keys() else str(
                                vals['start_date'])
                        vals['stop'] = str(end_time + timedelta(days=1))
                        vals["allday"] = values.get('allday') if \
                            'allday' in values.keys() else record.allday
                    else:
                        vals['start'] = str(values['start']) if \
                            'start' in values.keys() else str(vals['start'])
                        vals['stop'] = str(values['stop']) if \
                            'stop' in values.keys() else str(vals['stop'])

                    meeting_link = record.generate_meeting(
                        vals, attendees, active_user)
                    values['videocall_location'] = meeting_link.get('meeting_url')
                    values['teams_eventid'] = meeting_link.get('meeting_id')
                    values['description'] = meeting_link.get('meeting_body')

            elif values.get('teams_link_check') is False:
                if not active_user.is_authenticated:
                    raise ValidationError("Generate an access token to delete a Microsoft Teams meeting.")

                if record.write_uid == active_user:
                    record.delete_event(active_user)
                    values['description'] = ''
                    record.videocall_location = False
                else:
                    raise UserError(
                        "This Event can only Delete by Meeting Organizer")

            elif record.teams_link_check and record.videocall_location:
                if not active_user.is_authenticated:
                    raise ValidationError("Generate an access token to update a Microsoft Teams meeting.")

                if record.write_uid == active_user:
                    record.update_event(values, active_user)
                else:
                    raise UserError(
                        "This Event can only Update by Meeting Organizer")

        values['warning_check'] = False
        return super(TeamsCalendarEvent, self).write(values)

    def unlink(self):
        """Delete the Teams Meeting link with the unlink record"""
        active_user = self.env.user
        for rec in self:
            if rec.teams_link_check and rec.write_uid != active_user:
                raise UserError(
                    "This Event can only Delete by Meeting Organizer")
            elif rec.teams_link_check:
                rec.delete_event(active_user)

        return super(TeamsCalendarEvent, self).unlink()

    def generate_meeting(self, values, attendees, user):
        """Generate Microsoft Teams Meeting link
        Get new Access token if older one is expired
        """
        if user.is_authenticated:
            if user.token_expire:
                if user.token_expire <= datetime.now():
                    user.refresh_token()
            else:
                raise ValidationError("Generate new token for Microsoft teams meeting.")

        if user.teams_refresh_token and not user.teams_access_token:
            user.refresh_token()
        token = user.teams_access_token
        url = "https://graph.microsoft.com/v1.0/users/" + \
            "{}/calendar/events".format(user.email)
        header = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token)
            }
        if values.get('allday'):
            pass
        payload = {
            "subject": values.get('name'),
            "showAs": values.get('show_as'),
            "body": {
                "contentType": "HTML",
                "content": values.get('description')
                },
            "start": {
                "dateTime": values.get('start'),
                "timeZone": "UTC"
                },
            "end": {
                "dateTime": values.get('stop'),
                "timeZone": "UTC"
                },
            "location": {
                "displayName": "" if values.get(
                    'location') in [False, None] else values.get('location')
                },
            "attendees": attendees,
            "allowNewTimeProposals": True,
            "isOnlineMeeting": True,
            "onlineMeetingProvider": "teamsForBusiness",
            "isAllDay": values.get('allday')
            }
        try:
            meeting_obj = requests.request(
                "POST", url, headers=header, json=payload)

        except requests.exceptions.ConnectionError:
            _logger.exception("Could not establish the connection at %s", url)
            raise ValidationError(
                _("Could not establish the connection.")
                )

        except requests.exceptions.HTTPError:
            _logger.exception(
                "Invalid API request at %s", url
                )
            raise ValidationError(
                _(
                    "Webshipper: Invalid API request at %s",
                    url,
                    )
                )

        if meeting_obj.status_code in [201, 200]:
            meeting = meeting_obj.json().get('onlineMeeting')
            meeting_content = meeting_obj.json().get('body')
            return {
                "meeting_body": meeting_content.get(
                    'content') if meeting else '',
                "meeting_url": meeting.get('joinUrl') if meeting else False,
                "meeting_id": meeting_obj.json().get(
                    'id') if meeting else False
                }
        else:
            error_body = meeting_obj.json().get('error')

            error_message = "Error creating online meeting link" + \
                "\nStatus Code: %d \nReason: %s\n" % (
                    meeting_obj.status_code, meeting_obj.reason) + \
                        "Error: %s\nError Message: %s\n" % (
                            error_body.get('code'), error_body.get('message'))

            raise ValidationError(error_message)

    def update_event(self, values, user):
        """Update properties of existing Teams Meeting event. only meeting
        organizer(Who enables 'teams_link_check' boolean) can update event.
        """
        if user.is_authenticated:
            if user.token_expire:
                if user.token_expire <= datetime.now():
                    user.refresh_token()
            else:
                raise ValidationError("Generate new token for Microsoft teams meeting.")

        if user.teams_refresh_token and not user.teams_access_token:
            user.refresh_token()
        token = user.teams_access_token
        update_url = "https://graph.microsoft.com/" + \
            "v1.0/users/{0}/events/{1}".format(user.email, self.teams_eventid)

        header = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token)
            }

        rec_allday = False if values.get('allday') is False else self.allday

        if not any([values.get('allday'), rec_allday]):

            if values.get('allday') is False and  values.get('start') is None:
                start_on = str(self.start)
            else:
                start_on = str(
                    values['start']) if 'start' in values.keys() else False
            if values.get('allday') is False and  values.get('stop') is None:
                end_on = str(self.stop)
            else:
                end_on = str(
                    values['stop']) if 'stop' in values.keys() else False

        else:
            start_date = datetime.strptime(str(values['start_date']), '%Y-%m-%d') if 'start_date' in values.keys() else False
            end_date = datetime.strptime(str(values['stop_date']), '%Y-%m-%d') if 'stop_date' in values.keys() else False
            start_on = str(start_date) if start_date else False
            end_on = str(end_date + timedelta(days=1)) if end_date else False
        payload = {}
        if values.get('name'):
            payload.update({
                "subject": values.get('name')
                })
        if values.get('show_as'):
            payload.update({
                "showAs": values.get('show_as')
                })
        if values.get('description'):
            payload.update({
                "body": {
                    "content": values.get('description'),
                    "contentType": "HTML"
                    }
                })
        if start_on:
            payload.update({
                "start": {
                    "dateTime": start_on,
                    "timeZone": "UTC"
                    }
                })
        if end_on:
            payload.update({
                "end": {
                    "dateTime": end_on,
                    "timeZone": "UTC"
                    }
                })
        if values.get('location'):
            payload.update({
                "location": {
                    "displayName": values.get('location')
                    }
                })
        if 'partner_ids' in values.keys():
            payload.update({
                "attendees": self.prepare_attendee_vals(
                    values.get('partner_ids'))
                })
        if 'allday' in values.keys():
            payload.update({
                "isAllDay": values.get('allday')
                })
        if payload:
            try:
                update_response = requests.request(
                    "PATCH", update_url, headers=header, json=payload)

            except requests.exceptions.ConnectionError:
                _logger.exception(
                    "Could not establish the connection at %s", update_url)
                raise ValidationError(
                    _("Could not establish the connection.")
                    )

            except requests.exceptions.HTTPError:
                _logger.exception(
                    "Invalid API request at %s", update_url
                    )
                raise ValidationError(
                    _(
                        "Webshipper: Invalid API request at %s",
                        update_url,
                        )
                    )

            if update_response.status_code != 200:
                error_body = update_response.json().get('error')

                error_message = "Error updating online meeting" + \
                    "\nStatus Code: %d \nReason: %s\n" % (
                        update_response.status_code,
                        update_response.reason) + \
                            "Error: %s\nError Message: %s\n" % (
                                error_body.get('code'),
                                error_body.get('message'))

                raise ValidationError(error_message)

    def delete_event(self, user):
        """Delete existing Teams Meeting event.only meeting
        organizer(Who enables 'teams_link_check' boolean) can delete event.
        """
        if user.is_authenticated:
            if user.token_expire:
                if user.token_expire <= datetime.now():
                    user.refresh_token()
            else:
                raise ValidationError("Generate new token for Microsoft teams meeting.")
        else:
            raise ValidationError("Generate an access token to delete a Microsoft Teams meeting.")

        if user.teams_refresh_token and not user.teams_access_token:
            user.refresh_token()
        token = user.teams_access_token
        delete_url = "https://graph.microsoft.com/" + \
            "v1.0/users/{0}/events/{1}".format(user.email, self.teams_eventid)
        header = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token)
            }
        try:
            delete_response = requests.request(
                "DELETE", delete_url, headers=header)

        except requests.exceptions.ConnectionError:
            _logger.exception(
                "Could not establish the connection at %s", delete_url)
            raise ValidationError(
                _("Could not establish the connection.")
                )

        except requests.exceptions.HTTPError:
            _logger.exception(
                "Invalid API request at %s", delete_url
                )
            raise ValidationError(
                _(
                    "Webshipper: Invalid API request at %s",
                    delete_url,
                    )
                )

        if delete_response.status_code != 204:
            error_body = delete_response.json()
            error_message = "Error deleting online meeting" + \
                "\nStatus Code: %d \nReason: %s\n" % (
                    delete_response.status_code, delete_response.reason) + \
                        "Error: %s\nError Message: %s\n" % (
                            error_body.get('code'), error_body.get('message'))
            raise ValidationError(error_message)

    def prepare_attendee_vals(self, values):
        """
        Make a list of dictionary of participant's names and email addresses.
        """
        attendees = []
        res_partner = self.env['res.partner']
        for value in values:
            for partner in value[2]:
                attendees.append(
                    {
                        "emailAddress":
                        {
                            "address": res_partner.browse(partner).email,
                            "name": res_partner.browse(partner).name
                            },
                        "type": "required"
                        }
                    )
        return attendees

    def action_redirect_link(self):
        """Redirects to Teams Meeting Url.
        """
        if self.videocall_location:
            url = self.videocall_location
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new'
                }
