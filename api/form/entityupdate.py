#!/usr/bin/python3

import sys
import json
from flask import Flask, g, session, redirect, make_response
from flask import abort
from flask import Blueprint
from flask import request
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL

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

def create_parser_post():
    parser=reqparse.RequestParser()
    parser.add_argument('table',type=str, help='Name of the Datatable', location='query')
    parser.add_argument('id',type=str, help='ID from the datarow', location='query')
    return parser

class Entity(Resource):
    api=AppInfo.get_api()

    @api.doc(parser=create_parser_post())
    def post(self,table,id):
        try:
            create_parser_post().parse_args()
            context=g.context


            json=request.form.to_dict()
            for key in list(json):
                if key.startswith("__"):
                    del json[key]

            fetch=build_fetchxml_by_alias(context, table, id, json, type="update")
            fetchparser=FetchXmlParser(fetch, context)
            rs=DatabaseServices.exec(fetchparser,context, fetch_mode=0)

            next=HTTPRequest.redirect(request, default=f"/ui/v1.0/data/{table}/$$id$$", id=id)

            return redirect(next, code=302)

        except RestApiNotAllowed as err:
            logger.info(f"RestApiNotAllowed Exception: {err}")
            return redirect(f"/ui/login?redirect=/ui/v1.0/data/{table}/{id}", code=302)
        except Exception as err:
           return make_response(JinjaTemplate.render_status_template(500, err), 500)


def get_endpoint():
    return Entity
