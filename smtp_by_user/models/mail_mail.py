
import base64
import datetime
import logging
import psycopg2
import smtplib
import threading
import re

from collections import defaultdict

from odoo import _, api, fields, models
from odoo import tools
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def create(self, values):
        # notification field: if not set, set if mail comes from an existing mail.message
        if 'notification' not in values and values.get('mail_message_id'):
            values['notification'] = True

        outgoing_obj = None
        #create_user = self.create_uid.id if self.create_uid else self.env.uid
        for server_id in self.env['ir.mail_server'].search([]):
            _logger.error('**************************recorriendo servidores de correo*****************************')
            _logger.error(server_id)
            for user_id in server_id.user_ids:
                _logger.error('**************************recorriendo usuarios*****************************')
                _logger.error(user_id)
                _logger.error(self.env.uid)

                if self.env.uid == user_id.id:
                    _logger.error('**************************asignando servidor*****************************')
                    outgoing_obj = server_id

        if not outgoing_obj:
            outgoing_obj = self.env['ir.mail_server'].search([('is_default_server','=',True)],limit=1)

        if outgoing_obj:
            values['mail_server_id'] = outgoing_obj.id
            values['email_from'] = outgoing_obj.smtp_user

        _logger.error(values)

        new_mail = super(MailMail, self).create(values)
        if values.get('attachment_ids'):
            new_mail.attachment_ids.check(mode='read')
        return new_mail

    def send(self, auto_commit=False, raise_exception=False):
        """ Sends the selected emails immediately, ignoring their current
            state (mails that have already been sent should not be passed
            unless they should actually be re-sent).
            Emails successfully delivered are marked as 'sent', and those
            that fail to be deliver are marked as 'exception', and the
            corresponding error mail is output in the server logs.

            :param bool auto_commit: whether to force a commit of the mail status
                after sending each mail (meant only for scheduler processing);
                should never be True during normal transactions (default: False)
            :param bool raise_exception: whether to raise an exception if the
                email sending process has failed
            :return: True
        """
        for server_id, batch_ids in self._split_by_server():
            smtp_session = None
            try:
                for rec in self:
                    outgoing_obj = None
                    for server_id in self.env['ir.mail_server'].search([]):
                        for user_id in server_id.user_ids:
                            if rec.create_uid.id == user_id.id:
                                outgoing_obj = server_id

                    if not outgoing_obj:
                        outgoing_obj = self.env['ir.mail_server'].search([('is_default_server','=',True)],limit=1)

                    server_id = outgoing_obj.id
                    smtp_session = self.env['ir.mail_server'].connect(mail_server_id=server_id)
                    _logger.error('server_id-------------------------------------------------------')
                    _logger.error(server_id)
                    _logger.error('create_uid-------------------------------------------------------')
                    _logger.error(self.create_uid)
            except Exception as exc:
                if raise_exception:
                    # To be consistent and backward compatible with mail_mail.send() raised
                    # exceptions, it is encapsulated into an Odoo MailDeliveryException
                    raise MailDeliveryException(_('Unable to connect to SMTP Server'), exc)
                else:
                    batch = self.browse(batch_ids)
                    batch.write({'state': 'exception', 'failure_reason': exc})
                    batch._postprocess_sent_message(success_pids=[], failure_type="SMTP")
            else:
                self.browse(batch_ids)._send(
                    auto_commit=auto_commit,
                    raise_exception=raise_exception,
                    smtp_session=smtp_session)
                _logger.info(
                    'Sent batch %s emails via mail server ID #%s',
                    len(batch_ids), server_id)
            finally:
                if smtp_session:
                    smtp_session.quit()
