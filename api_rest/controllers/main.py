# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.base_rest.controllers import main


class BaseRestCsjPrivateApiController(main.RestController):
    _root_path = "/base_rest_api_rest/private/"
    _collection_name = "base.rest.csj.odoo.private.services"
    _default_auth = "user"
