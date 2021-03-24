# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ResCity(models.Model):
    _inherit = "res.city"

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.name + ' - ' + rec.state_id.name + ' - ' + rec.zipcode))
        return result


class ResCountryState(models.Model):
    _inherit = "res.country.state"

    dane_code = fields.Char('Código Dane', required="True")
