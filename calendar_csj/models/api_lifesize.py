# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import json
import random
import string

import logging

_logger = logging.getLogger(__name__)


class ApiLifesize(models.TransientModel):
    _name = "api.lifesize"
    _description = "Api Lifesize"

    def api_crud(self, vals):
        token_company = self.env.user.company_id.key_lifesize
        if not token_company:
            raise ValidationError("Please write token")

        def code(length=4, chars=string.digits):
            return "".join([random.choice(chars) for i in range(length)])

        def api_create(vals):
            url = "http://meetingapi.lifesizecloud.com" + "/meeting/create"
            try:
                description = vals.get("description").replace("\n", " - ")
            except:
                description = vals.get("description")
            body = {
                "displayName": vals.get("displayName"),
                "description": description,
                # "pin": code(),
                "ownerExtension": vals.get("ownerExtension"),
                "tempMeeting": "false",
                "hiddenMeeting": vals.get("hiddenMeeting"),
            }
            if vals.get("moderatorExtension"):
                body.update(
                    {"moderatorExtension": vals.get("moderatorExtension"),}
                )
            resp = requests.post(
                url=url,
                data=json.dumps(body),
                headers={"key": token_company, "Content-type": "application/json"},
            )
            if resp.ok:
                if not resp.json().get("errorDescription"):
                    res = resp.json()
                    resp.close
                    return res
                else:
                    resp.close
                    raise ValidationError(
                        "API message: {}".format(resp.json().get("errorDescription"))
                    )
            else:
                resp.close
                raise ValidationError("Bad response: %s." % (resp.json()))

        def api_read(vals):
            url = "http://meetingapi.lifesizecloud.com" + "/meeting/get"
            params = {
                "uuid": vals.get("uuid"),
            }
            resp = requests.get(
                url=url,
                params=params,
                headers={"key": token_company, "Content-type": "application/json"},
            )
            if resp.ok:
                res = resp.json()
                resp.close
                return res
            else:
                resp.close
                raise ValidationError("Bad response: %s." % (resp.json()))

        def api_update(body):
            url = "http://meetingapi.lifesizecloud.com" + "/meeting/update"
            del body["method"]
            # body = {
            #     "uuid": vals.get("uuid"), #Mandatory
            #     "description": vals.get("description"),
            #     "ownerExtension": vals.get("ownerExtension"),#Mandatory
            # }
            resp = requests.put(
                url=url,
                data=json.dumps(body),
                headers={"key": token_company, "Content-type": "application/json"},
            )
            if resp.ok:
                if not resp.json().get("errorDescription"):
                    res = resp.json()
                    resp.close
                    return res
                else:
                    resp.close
                    raise ValidationError(
                        "API message: {}".format(resp.json().get("errorDescription"))
                    )
            else:
                raise ValidationError("Bad response: %s." % (resp.json()))

        def api_delete(vals):
            url = "http://meetingapi.lifesizecloud.com" + "/meeting/delete"
            body = {
                "uuid": vals.get("uuid"),
            }
            resp = requests.delete(
                url=url,
                data=json.dumps(body),
                headers={"key": token_company, "Content-type": "application/json"},
            )
            if resp.ok:
                if not vals.get("errorDescription"):
                    res = resp.json()
                    resp.close
                    return res
                else:
                    raise ValidationError(
                        "API message: {}".format(resp.json().get("errorDescription"))
                    )
            else:
                raise ValidationError("Bad response: %s." % (resp.json()))

        def api_load(vals):
            url = "http://meetingapi.lifesizecloud.com" + "/meeting/load"
            params = {"limitSize": vals.get("number")}
            resp = requests.get(
                url=url,
                params=params,
                headers={"key": token_company, "Content-type": "application/json"},
            )
            if resp.ok:
                res = resp.json()
                resp.close
                return res
            else:
                raise ValidationError("Bad response: %s." % (resp.json()))

        if vals["method"] == "create":
            return api_create(vals)
        elif vals["method"] == "read":
            return api_read(vals)
        elif vals["method"] == "update":
            return api_update(vals)
        elif vals["method"] == "delete":
            return api_delete(vals)
        elif vals["method"] == "load":
            return api_load(vals)

    def api_user_crud(self, vals):
        token_company = self.env.user.company_id.key_lifesize

        if not token_company:
            raise ValidationError("Please write token")

        def api_Create(vals):
            url = "http://userapi.lifesizecloud.com/user" + "/createUser"
            body = {
                "email": vals.get("email"),
                "name": vals.get("name"),
                # "password": vals.get("password"), #In case that you want pass the password
                "password": "Password_LifeSize_User#2=",
            }
            resp = requests.post(
                url=url,
                data=json.dumps(body),
                headers={"key": token_company, "Content-type": "application/json"},
            )
            if resp.ok:
                if not vals.get("errorDescription"):
                    res = resp.json()
                    resp.close
                    return res
                else:
                    resp.close
                    raise ValueError("Api ERROR: %s." % (resp.json()))
            else:
                resp.close
                raise ValueError("Bad response: %s." % (resp.json()))

        def api_Search(vals):
            url = "http://userapi.lifesizecloud.com/user" + "/searchUser"
            params = {
                "email": vals.get("email"),
                # "uuid": vals.get("uuid"), #It is not necesary
            }
            resp = requests.get(
                url=url,
                params=params,
                headers={"key": token_company, "Content-type": "application/json"},
            )
            if resp.ok:
                res = resp.json()
                resp.close
                return res
            else:
                resp.close
                raise ValueError("Bad response: %s." % (resp.json()))

        def api_Update(body):
            url = "http://userapi.lifesizecloud.com/user" + "/updateUser"
            params = {
                "uuid": body.get("uuid"),
            }
            del [body["method"], body["uuid"]]
            resp = requests.put(
                url=url,
                params=params,
                data=json.dumps(body),
                headers={"key": token_company, "Content-type": "application/json",},
            )
            if resp.ok:
                res = resp.json()
                resp.close
                return res
            else:
                resp.close
                raise ValueError("Bad response: %s." % (resp.json()))

        def api_Delete(vals):
            url = "http://userapi.lifesizecloud.com/user" + "/deleteUser"
            body = {
                "uuid": vals.get("uuid"),
            }
            resp = requests.delete(
                url=url,
                data=json.dumps(body),
                headers={"key": token_company, "Content-type": "application/json"},
            )
            if resp.ok:
                res = resp.json()
                resp.close
                return res
            else:
                resp.close
                raise ValueError("Bad response: %s." % (resp.json()))

        if vals["method"] == "create":
            return api_Create(vals)
        elif vals["method"] == "search":
            return api_Search(vals)
        elif vals["method"] == "update":
            return api_Update(vals)
        elif vals["method"] == "delete":
            return api_Delete(vals)

    def resp2dict(self, resp):
        body = resp.get("body")
        if body.get("action") == "UPDATED":
            if not body.get("pin"):
                res = dict(
                    lifesize_modified=True, lifesize_pin=body.get("pin") or False
                )
                return res
        elif body.get("action") == "CREATED":
            res = dict(
                lifesize_pin=body.get("pin") or False,
                lifesize_uuid=body.get("uuid"),
                lifesize_url="https://call.lifesizecloud.com/{}".format(
                    body.get("extension")
                ),
                lifesize_meeting_ext=body.get("extension"),
                lifesize_owner=body.get("ownerExtension"),
                lifesize_moderator=body.get("moderatorExtension")
                if body.get("moderatorExtension")
                else body.get("moderatorUUID")
                if body.get("moderatorUUID")
                else False,
            )
            return res
