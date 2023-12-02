#!/usr/bin/python3
import sys
import json
from flask import Flask,request,abort, g, session, redirect, make_response, Blueprint
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL
from datetime import date, datetime

from core.appinfo import AppInfo
from core.fetchxmlparser import FetchXmlParser
from core.jsontools import json_serial
from core.exceptions import RestApiNotAllowed
from core import log

from services.httprequest import HTTPRequest
from services.fetchxml import build_fetchxml_by_alias
from services.database import DatabaseServices
from services.jinjatemplate import JinjaTemplate

logger=log.create_logger(__name__)

def create_parser():
    parser=reqparse.RequestParser()
    return parser


class EntityAdd(Resource):
    api=AppInfo.get_api()

    @api.doc(parser=create_parser())
    def post(self, table):
        try:
            context=g.context

            action="default"
            json=request.form.to_dict()
            for key in list(json):
                if key.startswith("__"):
                    if key=="__action":
                        action=json[key]
                    
                    del json[key]

            fetch=build_fetchxml_by_alias(context,table,None, json, type="insert")
            fetchparser=FetchXmlParser(fetch, context)
            rs=DatabaseServices.exec(fetchparser,context, fetch_mode=0)
            result={"rows_affected": rs.get_cursor().rowcount, "inserted_id": rs.get_inserted_id()}

            next=HTTPRequest.redirect(request, default=f"/ui/v1.0/data/{table}/{rs.get_inserted_id()}", id=rs.get_inserted_id())

            return redirect(next, code=302)

        except RestApiNotAllowed as err:
            logger.info(f"RestApiNotAllowed Exception: {err}")
            return redirect(f"/ui/login?redirect=/ui/v1.0/data/{table}", code=302)
        except Exception as err:
           return make_response(JinjaTemplate.render_status_template(context, 500, err), 500)

def get_endpoint():
    return EntityAdd
