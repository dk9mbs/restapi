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
    return parser

class AppHome(Resource):
    api=AppInfo.get_api("ui")

    @api.doc(parser=create_parser())
    def get(self):
        try:
            path="templates/base/uihome.htm"

            logger.info(f"Path: {path}")

            create_parser().parse_args()
            context=g.context

            template=JinjaTemplate.create_file_template(context, path)

            fetch=f"""
            <restapi type="select">
                <table name="api_ui_app" alias="a"/>
                <select>
                    <field name="id" table_alias="a"/>
                    <field name="name" table_alias="a"/>
                    <field name="description" table_alias="a"/>
                    <field name="home_url" table_alias="a"/>
                </select>
            </restapi>
            """
            fetch_parser=FetchXmlParser(fetch,context)
            rs=DatabaseServices.exec(fetch_parser, context, fetch_mode=0)

            response = make_response(template.render({"context": context, "apps":rs.get_result() }))
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
    return AppHome
