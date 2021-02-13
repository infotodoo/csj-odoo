# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    #out_mail_server_ids = fields.Many2many('ir.mail_server', 'Outgoing mail servers')
    out_mail_server_id = fields.Many2one('ir.mail_server', 'Servidor de Correo de Salida')
    
