# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, tools
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

class CalendarAppointmentReport(models.Model):
    _name = "calendar.appointment.report"
    _auto = False
    _rec_name = 'calendar_datetime'
    _order = 'calendar_datetime desc'

    appointment_code = fields.Char('ID SOLICITUD')
    request_type_label = fields.Char('TIPO DE SOLICITUD')
    type_request_concatenated = fields.Char('CONCATENADO')
    type = fields.Char('SOLICITUD')
    calendar_date = fields.Char('FECHA DE REALIZACIÓN')
    calendar_time = fields.Char('HORA DE INICIO')
    judged_only_code = fields.Char('CÓDIGO DESPACHO SOLICITANTE')
    judged_only_name = fields.Char('DESPACHO SOLICITANTE')
    city_id = fields.Char('ORIGEN')
    country_state_id = fields.Char('DEPARTAMENTO')
    destination_ids_label = fields.Char('DESTINO')
    reception_id = fields.Char('MEDIO DE RECEPCIÓN')
    reception_detail = fields.Char('DETALLE MEDIO DE RECEPCIÓN')
    observations = fields.Char('OBSERVACIONES')
    request_date = fields.Char('FECHA DE SOLICITUD')
    applicant_id = fields.Char('NOMBRE DEL SOLICITANTE')
    state = fields.Char('ESTADO')
    applicant_email = fields.Char('CORREOS SOLICITANTE')
    process_number = fields.Char('NÚMERO DE PROCESO')
    room_id_mame = fields.Char('SALA')
    partner_ids_label = fields.Char('PARTICIPANTES')
    applicant_mobile = fields.Char('CELULAR')
    class_id = fields.Char('CLASE DE VIDEOCONFERENCIA')
    request_type = fields.Char('TIPO DE AUDIENCIA')
    appointment_date = fields.Char('FECHA AGENDAMIENTO')
    create_uid_login = fields.Char('USUARIO AGENDAMIENTO')
    appointment_close_date = fields.Char('FECHA DE CIERRE')
    appointment_close_user_login = fields.Char('USUARIO DE CIERRE')
    end_date = fields.Char('FECHA FINAL')
    end_hour = fields.Char('HORA FINAL')
    state_description = fields.Char('DESCRIPCION')
    tag_number = fields.Char('ETIQUETA')
    link_download = fields.Char('URL DE GRABACIÓN')
    link_download_text = fields.Char('URL DE GRABACIÓN TEXT')
    create_uid = fields.Char('CREADOR POR')
    name = fields.Char('NOMBRE DE LA SALA LIFESIZE')
    lifesize_url = fields.Char('URL LIFESIZE')
    teams_url = fields.Char('URL TEAMS')
    calendar_datetime = fields.Char('FECHA Y HORA DE REALIZACIÓN')


    def init(self):
        #tools.drop_view_if_exists(self._cr, 'calendar_appointment_report')
        query = """

                SELECT 
                row_number() OVER () as id,
                ca.appointment_code,
                (ch1.name || ' ' || ch2.name || ' ' || ch3.name)::text as request_type_label,

                (CASE 
                    WHEN ch2.id is null THEN ch1.name
                    WHEN ch1.id is null THEN ch2.name
                    WHEN ch1.id is not null and ch2.id is not null THEN ch2.name || ' ' || ch1.name
                    ELSE ''
                END)::text as type_request_concatenated,

                (CASE
                    WHEN ca.type = 'audience' THEN 'AUDIENCIA'
                    WHEN ca.type = 'conference' THEN 'CONFERENCIA'
                    WHEN ca.type = 'streaming' THEN 'Streaming'
                    ELSE ''
                END) as type,

                DATE(ca.calendar_datetime) as calendar_date,
                EXTRACT(HOUR FROM ca.calendar_datetime) AS calendar_time,
                --ca.calendar_datetime as calendar_time,

                (CASE
                    WHEN partner.id is not null
                    THEN city.zipcode || entity.code || specialty.code || partner.code
                    ELSE ''
                END) judged_only_code,

                ca.judged_only_name,
                city.name as city_id,
                state.name as country_state_id,
                ca.destination_ids_label,
                reception.name as reception_id,
                ca.reception_detail,
                ca.observations,
                ca.request_date,
                applicant.name as applicant_id,

                (CASE 
                    WHEN ca.state = 'open' THEN 'AGENDADO'
                    WHEN ca.state = 'realized' THEN 'REALIZADA'
                    WHEN ca.state = 'unrealized' THEN 'NO REALIZADA'
                    WHEN ca.state = 'postpone' THEN 'APLAZADA'
                    WHEN ca.state = 'assist_postpone' THEN 'ASISTIDA Y APLAZADA'
                    WHEN ca.state = 'assist_cancel' THEN 'ASISTIDA Y CANCELADA'
                    WHEN ca.state = 'cancel' THEN 'CANCELADO'
                    WHEN ca.state = 'draft' THEN 'BORRADOR'
                    ELSE ''
                END) as state,

                (CASE
                    WHEN applicant.email is not null THEN applicant.email ELSE ''
                END) as applicant_email,
                --ca.applicant_email,

                ca.process_number,
                room.name as room_id_mame,
                ca.partner_ids_label,

                (CASE
                    WHEN applicant.email is not null THEN applicant.mobile ELSE ''
                END) as applicant_mobile,

                class.name as class_id,
                (CASE
                    WHEN ca.request_type = 'l' THEN 'L'
                    WHEN ca.request_type = 'r' THEN 'R'
                    ELSE ''
                END) as request_type,

                ca.appointment_date,
                usuario.login as create_uid_login,
                ca.appointment_close_date,
                user_close.login as appointment_close_user_login,
                ca.end_date,
                ca.end_hour,
                ca.state_description,

                (CASE
                    WHEN
                        city.id is not null and
                        city.zipcode is not null and
                        (room.id is not null or ca.type != 'audience') and
                        ca.process_number is not null and ca.partner_id is not null and
                        entity.id is not null and partner.specialty_id is not null
                        and partner.code is not null
                    THEN
                        ca.process_number || upper(ca.request_type) || city.zipcode || entity.code || specialty.code || partner.code
                        || room.code || (CASE WHEN ca.calendar_datetime is not null THEN '_' || 

                        (CASE
                            WHEN ca.calendar_datetime is not null
                            THEN
                                '01_' || TO_CHAR(ca.calendar_datetime - interval '5 hours', 'YYYY-MM-DD HH24:MI:SS') || '_V'
                            ELSE ''
                        END)

                        ELSE '' END) 
                    ELSE
                        'Configurar los valores'
                END) as tag_number,
                ca.link_download,
                ('"' || ca.link_download || '"')::text as link_download_text,
                ca.create_uid,
                ca.name,
                ca.lifesize_url,
                ca.teams_url,
                ca.calendar_datetime
                FROM calendar_appointment ca
                LEFT JOIN calendar_help ch1 on ca.partaker_type = ch1.id
                LEFT JOIN calendar_help ch2 on ca.help_id = ch2.id
                LEFT JOIN calendar_help ch3 on ca.connection_type = ch3.id
                LEFT JOIN res_partner applicant on ca.applicant_id = applicant.id
                LEFT JOIN res_judged_room room on ca.room_id = room.id
                LEFT JOIN res_users usuario on ca.create_uid = usuario.id
                LEFT JOIN res_users user_close on ca.appointment_close_user_id = user_close.id
                LEFT JOIN calendar_appointment_type cat on ca.appointment_type_id = cat.id
                LEFT JOIN res_partner partner on cat.judged_id = partner.id
                LEFT JOIN res_city city on partner.city_id = city.id
                LEFT JOIN res_country_state state on city.state_id = state.id
                LEFT JOIN res_specialty specialty on partner.specialty_id = specialty.id
                LEFT JOIN res_entity entity on specialty.entity_id = entity.id
                LEFT JOIN calendar_reception reception on ca.reception_id = reception.id
                LEFT JOIN calendar_class class on ca.class_id = class.id

                where 1=1
            """
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, query))
