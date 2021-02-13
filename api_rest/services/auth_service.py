
# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import odoo
from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component
from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime
import logging
import json


import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi
from werkzeug import urls
from werkzeug.wsgi import wrap_file


_logger = logging.getLogger(__name__)


class ServiceAuth(Component):
    _inherit = "base.rest.service"
    _name = "user.auth.service"
    _usage = "ValidateToken"
    _collection = "base.rest.csj.odoo.private.services"
    _description = """
        Judged Auth Services
        Access to the Judged Auth Services is only allowed to authenticated partners.
        If you are not authenticated go to <a href='/web/login'>Login</a>
    """

    '''
    def get(self, _id):
        """
        Get Token Session
        """
        partner = self.env["res.partner"].browse(_id)
        return self._to_json(partner)
    '''

    def search(self, name):
        """
        Searh Token Session
        """

        path = odoo.tools.config.session_dir
        _logger.error(path)
        
        result = werkzeug.contrib.sessions.FilesystemSessionStore(
            path, session_class=name, renew_missing=False)
        _logger.error('----------------------dir--------------')
        _logger.error(dir(result))
        _logger.error('----------------------validate key--------------')
        _logger.error(result.is_valid_key(name))

        if result.is_valid_key(name):
            res = {
                "id": name,
                "name": 'Token Valido',
                "code": 'True',
            }
        else:
            res = {
                "id": name,
                "name": 'Token NO Valido',
                "code": 'False',
            }
        rows = []
        rows.append(res)
        res = {"count": 1, "rows": rows}
        return res

    #def _get(self, _id):
    #    return self.env["res.partner"].browse(_id)

    #def _get_document(self, _id):
    #    return self.env["res.partner"].browse(_id)

    # Validator
    def _validator_return_get(self):
        res = self._validator_create()
        #res.update({"id": {"type": "integer", "required": False, "empty": False}})
        return res

    def _validator_search(self):
        return {"name": {"type": "string", "nullable": False, "required": True}}

    def _validator_return_search(self):
        return {
            "count": {"type": "integer", "required": True},
            "rows": {
                "type": "list",
                "required": False,
                "schema": {"type": "dict", "schema": self._validator_return_get()},
            },
        }

    def _validator_create(self):
        res = {
            "name": {"type": "string", "required": False, "empty": True},
            "code": {"type": "string", "required": False, "empty": True},
        }
        return res

    def _validator_return_create(self):
        return self._validator_return_get()

    def _validator_update(self):
        res = self._validator_create()
        for key in res:
            if "required" in res[key]:
                del res[key]["required"]
        return res

    def _validator_return_update(self):
        return self._validator_return_get()

    def _validator_archive(self):
        return {}

    def _to_json(self, partner):
        res = {
            "id": partner.id,
            "name": partner.name,
            "code": partner.code,
        }
        return res

