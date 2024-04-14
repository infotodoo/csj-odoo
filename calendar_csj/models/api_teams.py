# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta
import requests
import urllib.parse
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import string

_logger = logging.getLogger(__name__)


class ApiTeams(models.TransientModel):
    _name = "api.teams"
    _description = "Api Teams"

    def api_crud(self, vals):
        token_company = self.env['res.users'].browse(2).teams_access_token
        if not token_company:
            raise ValidationError("Please write token")

        def code(length=4, chars=string.digits):
            return "".join([random.choice(chars) for i in range(length)])

        def api_create(vals):
            """Call Function to generate Teams Meeting link with appropriate
            Time format and time zone if 'teams_link_check' is True.
            """
            active_user = self.env['res.users'].browse(2)
            """Generate Microsoft Teams Meeting link
            Get new Access token if older one is expired
            """
            active_user.refresh_token()
            if active_user.is_authenticated:
                if active_user.token_expire:
                    if active_user.token_expire <= datetime.now():
                        active_user.refresh_token()
                else:
                    raise ValidationError("Generar nuevo token para el agendamiento usando Microsoft Teams.")

            if active_user.teams_refresh_token and not active_user.teams_access_token:
                active_user.refresh_token()
            token = active_user.teams_access_token

            # Primero obtenemos el ID del usuario con el que vamos a crear los teams
            url = f"https://graph.microsoft.com/v1.0/users/{self.env.user.company_id.client_email}"
            # Encabezados de la solicitud
            headers = {
                "Authorization": f"Bearer {token}"
            }
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Verificar si hay errores en la respuesta HTTP
                user_data = response.json()
                user_id = user_data.get('id')
            except requests.exceptions.RequestException as e:
                raise ValidationError(f"No se pudo obtener el ID del usuario: {e}")

            judged_id = self.env['res.partner'].browse(int(vals.get('judged_id')))

            if not active_user.is_authenticated:
                raise ValidationError("Genere un token de acceso para crear una reunión de Microsoft Teams")
            attendees = self.prepare_attendee_vals(vals.get('partner_ids'))

            tenantId = "622cba98-80f8-41f3-8df5-8eb99901598b"
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}/onlineMeetings"
            header = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(token)
            }
            try:
                description = vals.get("description").replace("\n", " - ")
            except:
                description = vals.get("description")

            # Convertir las cadenas de fecha y hora a objetos datetime
            start_datetime = datetime.strptime(vals.get('start'), '%Y-%m-%d %H:%M:%S')
            end_datetime = datetime.strptime(vals.get('stop'), '%Y-%m-%d %H:%M:%S')

            # Aplicar la zona horaria UTC a las fechas y horas
            start_datetime_utc = start_datetime.replace(tzinfo=pytz.timezone('UTC'))
            end_datetime_utc = end_datetime.replace(tzinfo=pytz.timezone('UTC'))

            # Formatear las fechas y horas en el nuevo formato
            formatted_start = start_datetime_utc.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            formatted_end = end_datetime_utc.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

            payload = {
                "creationDateTime": formatted_start,
                "startDateTime": formatted_start,
                "endDateTime": formatted_end,
                "isBroadcast": False,
                "autoAdmittedUsers": "everyone",
                "outerMeetingAutoAdmittedUsers": "everyone",
                "capabilities": [],
                "externalId": None,
                "iCalUid": None,
                "meetingType": None,
                "meetingsMigrationMode": None,
                "subject": vals.get("displayName") if vals.get("displayName") else None,
                "videoTeleconferenceId": None,
                "isEntryExitAnnounced": False,
                "allowedPresenters": "roleIsPresenter",
                "allowAttendeeToEnableMic": True,
                "allowAttendeeToEnableCamera": True,
                "allowMeetingChat": "enabled",
                "shareMeetingChatHistoryDefault": "none",
                "allowTeamworkReactions": True,
                "anonymizeIdentityForRoles": [],
                "recordAutomatically": False,
                "allowParticipantsToChangeName": False,
                "allowTranscription": True,
                "allowRecording": True,
                "meetingTemplateId": None,
                "broadcastSettings": None,
                "meetingInfo": vals.get("description") if vals.get("description") else None,
                "audioConferencing": None,
                "watermarkProtection": None,
                "chatRestrictions": None,
                "participants": {
                    "organizer": {
                        "upn": self.env.user.company_id.client_email,
                        "role": "presenter",
                        "identity": {
                            "application": None,
                            "device": None,
                            "user": {
                                "id": user_id,
                                "displayName": None,
                                "tenantId": tenantId,
                                "identityProvider": "AAD"
                            }
                        }
                    },
                    "attendees": [
                        {
                            "upn": judged_id.email,
                            "role": "coorganizer",
                        },
                        {
                            "upn": judged_id.email,
                            "role": "presenter",
                        },
                    ]
                }
            }
            _logger.error(payload)
            try:
                meeting_obj = requests.request(
                    "POST", url, headers=header, json=payload)
            except requests.exceptions.ConnectionError:
                _logger.exception("No se pudo establecer la conexión en %s", url)
                raise ValidationError(
                    _("No se pudo establecer la conexión con Microsoft Teams.")
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
                meeting = meeting_obj.json()
                #_logger.error(meeting.get('joinUrl'))
                # Decodificar el contenido
                decoded_content = urllib.parse.unquote(meeting.get('joinInformation').get('content'))
                meeting_id = meeting.get('meetingCode')
                join_url = meeting.get('joinUrl')
                organizer_id = user_id
                tenant_id = tenantId
                thread_id = meeting.get('chatInfo').get('threadId')
                content_html = """
                    <div style="max-width: 520px; color: #242424; font-family:'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif" class="me-email-text">
                    <div style="margin-bottom:24px;overflow:hidden;white-space:nowrap;">________________________________________________________________________________</div>

                    <div style="margin-bottom:12px;">
                        <span class="me-email-text" style="font-size: 24px;font-weight: 700;margin-right:12px;">Reunión de Microsoft Teams</span>
                        <a id="meet_invite_block.action.help" class="me-email-link" style="font-size:14px;text-decoration:underline;color: #5B5FC7;" href="https://aka.ms/JoinTeamsMeeting?omkt=en-US">Necesita Ayuda?</a>
                    </div>
                    <div style="margin-top:0px; margin-bottom:0px; font-weight:bold">
                        <span style="font-size:14px; color:#252424">
                            Únase a través de su ordenador, aplicación móvil o dispositivo de sala
                        </span>
                    </div>
                    <div style="margin-bottom:6px;">
                        <a id="meet_invite_block.action.join_link" class="me-email-headline" style="font-size: 20px;font-weight:600;text-decoration:underline;color: #5B5FC7;" href="{joinUrl}" target="_blank" rel="noreferrer noopener">
                            Haga clic aquí para unirse a la reunión
                        </a>
                    </div>
                    <div style="margin-bottom:6px;">
                        <span class="me-email-text-secondary" style="font-size: 14px;color: #616161;">
                            ID de la reunión: <b>{meeting_id}</b>
                        </span>
                    </div>
                    <div style="font-size:14px">
                        <a href="https://www.microsoft.com/en-us/microsoft-teams/download-app" class="me-email-link" style="font-size:14px; text-decoration:underline;color:#6264a7; font-family:'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif">
                            Descargar Teams
                        </a>
                        <a href="https://www.microsoft.com/microsoft-teams/join-a-meeting" class="me-email-link" style="font-size:14px; text-decoration:underline; color:#6264a7; font-family:'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif">
                            Unirse en la web
                        </a>
                    </div>
                    <div>
                        <span class="me-email-text-secondary" style="font-size: 14px;color: #616161;">Para organizadores: </span>
                        <a id="meet_invite_block.action.organizer_meet_options" class="me-email-link" style="font-size: 14px;text-decoration:underline;color: #5B5FC7;" target="_blank" href="https://teams.microsoft.com/meetingOptions/?organizerId={organizer_id}&tenantId={tenant_id}&threadId={thread_id}&messageId=0&language=en-US" rel="noreferrer noopener">
                            Opciones de la réunion
                        </a>
                        <span style="color: #D1D1D1">|</span>
                        <a id="meet_invite_block.action.organizer_reset_dialin_pin" class="me-email-link" style="font-size: 14px;text-decoration:underline;color: #5B5FC7;" target="_blank" href="https://dialin.teams.microsoft.com/usp/pstnconferencing" rel="noreferrer noopener">
                            Reset dial-in PIN
                        </a>
                    </div>
                """.format(meeting_id=meeting_id, joinUrl=join_url, organizer_id=organizer_id, tenant_id=tenant_id, thread_id=thread_id)

                return {
                    "meeting_body": content_html if content_html else '',
                    "meeting_url": join_url if join_url else False,
                    "meeting_id": meeting_id if meeting_id else False,
                    "action": 'CREATED'
                }
            else:
                error_body = meeting_obj.json().get('error')
                error_message = "Error creating online meeting link" + \
                    "\nStatus Code: %d \nReason: %s\n" % (
                        meeting_obj.status_code, meeting_obj.reason) + \
                            "Error: %s\nError Message: %s\n" % (
                                error_body.get('code'), error_body.get('message'))

                raise ValidationError(error_message)

        def api_update(values):
            """Update properties of existing Teams Meeting event. only meeting
            organizer(Who enables 'teams_link_check' boolean) can update event.
            """
            active_user = self.env['res.users'].browse(2)
            if self.env.user.is_authenticated:
                if active_user.token_expire:
                    if active_user.token_expire <= datetime.now():
                        active_user.refresh_token()
                else:
                    raise ValidationError("Generate new token for Microsoft teams meeting.")

            if active_user.teams_refresh_token and not active_user.teams_access_token:
                active_user.refresh_token()
            token = active_user.teams_access_token
            update_url = "https://graph.microsoft.com/" + \
                "v1.0/users/{0}/events/{1}".format(self.env.user.company_id.client_email, vals.get('teams_uuid'))

            header = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(token)
                }

            payload = {}
            if values.get('name'):
                payload.update({
                    "subject": values.get('name')
                    })
            if values.get('show_as'):
                payload.update({
                    "showAs": 'busy'
                    })
            if values.get('description'):
                payload.update({
                    "body": {
                        "content": values.get('description'),
                        "contentType": "HTML"
                        }
                    })
            if values.get('start'):
                payload.update({
                    "start": {
                        "dateTime": values.get('start'),
                        "timeZone": "UTC"
                        }
                    })
            if values.get('stop'):
                payload.update({
                    "end": {
                        "dateTime": values.get('stop'),
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


        def api_delete(vals):
            """Delete existing Teams Meeting event.only meeting
            organizer(Who enables 'teams_link_check' boolean) can delete event.
            """
            active_user = self.env['res.users'].browse(2)
            if self.env.user.is_authenticated:
                if active_user.token_expire:
                    if active_user.token_expire <= datetime.now():
                        active_user.refresh_token()
                else:
                    raise ValidationError("Generate new token for Microsoft teams meeting.")
            else:
                raise ValidationError("Generate an access token to delete a Microsoft Teams meeting.")

            if active_user.teams_refresh_token and not active_user.teams_access_token:
                active_user.refresh_token()
            token = active_user.teams_access_token
            delete_url = "https://graph.microsoft.com/" + \
                "v1.0/users/{0}/events/{1}".format(self.env.user.company_id.client_email, vals.get('teams_uuid'))
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


        if vals["method"] == "create":
            return api_create(vals)
        elif vals["method"] == "update":
            return api_update(vals)
        elif vals["method"] == "delete":
            return api_delete(vals)


    def resp2dict(self, resp):
        if resp.get("action") == "UPDATED":
            res = dict(lifesize_modified=True,)
            return res
        elif resp.get("action") == "CREATED":
            res = dict(
                teams_url=resp.get("meeting_url"),
                teams_uuid=resp.get("meeting_id"),
                teams_description=resp.get("meeting_body"),
            )
            return res

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
                        "type": "required",
                        #"roles": "owner",
                        }
                    )
        return attendees

