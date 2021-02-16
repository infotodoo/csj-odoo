# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

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

class MailMailInherit(models.Model):

    _name = 'mail.mail'
    _inherit = 'mail.mail'

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
        if not self.ids:
            limit = self.env['ir.config_parameter'].sudo().get_param('mail.send_limit','28')
            _logger.info("======= sending emails with limit=%s" % limit)
            filters = ['&',
                       ('state', '=', 'outgoing'),
                       '|',
                       ('scheduled_date', '<', datetime.datetime.now()),
                       ('scheduled_date', '=', False)]
            if 'filters' in self._context:
                filters.extend(self._context['filters'])
            ids = self.search(filters, limit=int(limit)).ids
        res = None
        try:
            # auto-commit except in testing mode
            auto_commit = not getattr(threading.currentThread(), 'testing', False)
            res = self.browse(ids).send(auto_commit=auto_commit)
        except Exception:
            _logger.exception("Failed processing mail queue")
        return res
