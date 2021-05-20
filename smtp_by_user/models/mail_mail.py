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
            for user_id in server_id.user_ids:
                if self.env.uid == user_id.id:
                    outgoing_obj = server_id

        if not outgoing_obj:
            outgoing_obj = self.env['ir.mail_server'].search([('is_default_server','=',True)],limit=1)

        if outgoing_obj:
            values['mail_server_id'] = outgoing_obj.id
            values['email_from'] = outgoing_obj.smtp_user

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




    @api.model
    def process_email_queue(self, ids=None):
        """Send immediately queued messages, committing after each
           message is sent - this is not transactional and should
           not be called during another transaction!

           :param list ids: optional list of emails ids to send. If passed
                            no search is performed, and these ids are used
                            instead.
           :param dict context: if a 'filters' key is present in context,
                                this value will be used as an additional
                                filter to further restrict the outgoing
                                messages to send (by default all 'outgoing'
                                messages are sent).
        """
        res = None
        for server_id in self.env['ir.mail_server'].search([('active','=',True)]):
            smtp_session = None
            raise_exception=False
            if not self.ids:
                batch_total_max = 0
                sys_params = self.env['ir.config_parameter'].sudo()
                limit = int(sys_params.get_param('mail.session.batch.size', 22))
                ids = []
                _logger.info("======= sending emails with limit=%s" % limit)
                filters = ['&','&',
                           ('state', '=', 'outgoing'),
                           ('mail_server_id', '=', server_id.id),
                           '|',
                           ('scheduled_date', '<', datetime.datetime.now()),
                           ('scheduled_date', '=', False)]
                if 'filters' in self._context:
                    filters.extend(self._context['filters'])
                ids = self.search(filters, order='scheduled_date asc', limit=int(limit)).ids
                #ids.sort()
                _logger.error('*********** PROCESANDO SERVER MAIL RECORDS ************')
                _logger.error(ids)

            if ids:
                try:
                    smtp_session = self.env['ir.mail_server'].connect(mail_server_id=server_id.id)
                except Exception as exc:
                    if raise_exception:
                        # To be consistent and backward compatible with mail_mail.send() raised
                        # exceptions, it is encapsulated into an Odoo MailDeliveryException
                        raise MailDeliveryException(_('Unable to connect to SMTP Server'), exc)
                    else:
                        batch = self.browse(ids)
                        batch.write({'state': 'exception', 'failure_reason': exc})
                        batch._postprocess_sent_message(success_pids=[], failure_type="SMTP")
                else:
                    auto_commit = not getattr(threading.currentThread(), 'testing', False)
                    self.browse(ids)._send(
                        auto_commit=auto_commit,
                        raise_exception=raise_exception,
                        smtp_session=smtp_session)
                    _logger.info(
                        'Sent batch %s emails via mail server ID #%s',
                        len(ids), server_id)
                finally:
                    if smtp_session:
                        smtp_session.quit()
