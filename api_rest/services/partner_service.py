# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component



class PartnerService(Component):
    _inherit = "base.rest.service"
    _name = "partner.service"
    _usage = "partner"
    _collection = "base.rest.livingston.test.private.services"
    _description = """
        Partner Services
        Access to the partner services is only allowed to authenticated users.
        If you are not authenticated go to <a href='/web/login'>Login</a>
    """
    
    def get(self, _id):
        """
        Get partner's informations
        """
        return self._to_json(self._get(_id))
    

    def search(self, name):
        """
        Searh partner by name
        """
        partners = self.env["res.partner"].name_search(name)
        partners = self.env["res.partner"].browse([i[0] for i in partners])
        rows = []
        res = {"count": len(partners), "rows": rows}
        for partner in partners:
            rows.append(self._to_json(partner))
        return res

    
    # pylint:disable=method-required-super
    def create(self, **params):
        """
        Create a new partner
        """
        partner = self.env["res.partner"].create(self._prepare_params(params))
        return self._to_json(partner)

    def update(self, _id, **params):
        """
        Update partner informations
        """
        partner = self._get(_id)
        partner.write(self._prepare_params(params))
        return self._to_json(partner)

    

    # The following method are 'private' and should be never never NEVER call
    # from the controller.

    def _get(self, _id):
        return self.env["res.partner"].browse(_id)

    def _get_document(self, _id):
        return self.env["res.partner"].browse(_id)
    #"country", "state"

    def _prepare_params(self, params):
        for key in ["country", "state", "property_account_receivable","property_account_payable"]:
            if key in params:
                val = params.pop(key)
                if val.get("id"):
                    params["%s_id" % key] = val["id"]
        return params

    # Validator
    def _validator_return_get(self):
        res = self._validator_create()
        res.update({"id": {"type": "integer", "required": True, "empty": False}})
        return res

    def _validator_search(self):
        return {"name": {"type": "string", "nullable": False, "required": True}}
    
 
        
    def _validator_return_search(self):
        return {
            "count": {"type": "integer", "required": True},
            "rows": {
                "type": "list",
                "required": True,
                "schema": {"type": "dict", "schema": self._validator_return_get()},
            },
        }
    


    def _validator_create(self):
        res = {
            "id" : {"type": "integer", "coerce": to_int, "nullable": True},
            "person_type":{"type": "string", "required": True, "empty": False},
            "name": {"type": "string", "required": True, "empty": False},
            "street": {"type": "string", "required": True, "empty": False},
            "street2": {"type": "string", "nullable": True},
            "zip" : {"type": "string", "required": True, "empty": False},
            "city": {"type": "string", "required": True, "empty": False},
            "state": {
                "type": "dict",
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    "name": {"type": "string"},
                },
            },
            "country": {
                "type": "dict",
                "schema": {
                    "id": {
                        "type": "integer",
                        "coerce": to_int,
                        "required": True,
                        "nullable": False,
                    },
                    "name": {"type": "string"},
                },
            },
            "property_account_receivable":{
                "type": "dict",
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    "name": {"type": "string"},
                },
            },
            "property_account_payable":{
                "type": "dict",
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    "name": {"type": "string"},
                },
            },           
            "is_company": {"coerce": to_bool, "type": "boolean"},

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
            "id" : partner.id,
            "person_type" : partner.person_type,
            "name": partner.name,
            "street": partner.street,
            "street2": partner.street2 or "",
            "zip": partner.zip,
            "city": partner.city,     
            "is_company" : partner.is_company,
        }

        if partner.country_id:
            res["country"] = {
                "id": partner.country_id.id,
                "name": partner.country_id.name,
            }
        if partner.state_id:
            res["state"] = {
                "id": partner.state_id.id,
                "name": partner.state_id.name
            }
        #here 

        if partner.property_account_receivable_id:
            res["property_account_receivable"] = {
                "id": partner.property_account_receivable_id.id,
                "name": partner.property_account_receivable_id.name,
            }

        if partner.property_account_payable_id:
            res["property_account_payable"] = {
                "id": partner.property_account_payable_id.id,
                "name": partner.property_account_payable_id.name,
            }
        
        return res
