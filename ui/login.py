#!/usr/bin/python3

import sys
import json
import jinja2
import os
import urllib
from flask import Flask, g, session, redirect, abort,request,Blueprint
from flask import make_response, send_file
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL

from services.fetchxml import build_fetchxml_by_alias
from services.database import DatabaseServices
from services.httprequest import HTTPRequest
from services.filesystemtools import FileSystemTools
from services.jinjatemplate import JinjaTemplate

from core.appinfo import AppInfo
from core.fetchxmlparser import FetchXmlParser
from core.jsontools import json_serial
from core import log
from core.exceptions import RestApiNotAllowed, ConfigNotValid

logger=log.create_logger(__name__)

def create_parser():
    parser=reqparse.RequestParser()
    parser.add_argument('restapi_username',type=str, help='Username', location='query')
    parser.add_argument('restapi_password',type=str, help='Password', location='query')
    return parser

class Portal(Resource):
    api=AppInfo.get_api("ui")

    @api.doc(parser=create_parser())
    def get(self):
        try:
            path="templates/base/login.htm"

            logger.info(f"Path: {path}")

            create_parser().parse_args()
            context=g.context

            next=HTTPRequest.redirect(request, "/ui/login")
            logger.info(f"Redirect : {next}")

            msg=''
            if 'msg' in request.args:
                msg=request.args.get('msg')

            logged_on=False
            if 'session_id' in session:
                try:
                    g.context=AppInfo.create_context(session['session_id'])
                    logged_on=True
                except NameError as err:
                    logged_on=False

            template=JinjaTemplate.create_file_template(context, path)

            response = make_response(template.render({"redirect": next, "msg": msg, "logged_on": logged_on, "context": context}))
            response.headers['content-type'] = 'text/html'

            return response

        except ConfigNotValid as err:
            logger.exception(f"Config not valid {err}")
            return make_response(JinjaTemplate.render_status_template(500, err), 500)
        except jinja2.exceptions.TemplateNotFound as err:
            logger.exception(f"TemplateNotFound: {err}")
            return make_response(JinjaTemplate.render_status_template(404, f"Template not found {err}"), 404)
        except FileNotFoundError as err:
            logger.exception(f"FileNotFound: {err}")
            return make_response(JinjaTemplate.render_status_template(404, f"File not found {err}"), 404)
        except RestApiNotAllowed as err:
            logger.exception(f"RestApiNotAllowed Exception: {err}")
            return redirect(f"/ui/login?redirect={request.url}", code=302)
        except Exception as err:
            logger.exception(f"Exception: {err}")
            return make_response(JinjaTemplate.render_status_template(500, err), 500)

def get_endpoint():
    return Portal
