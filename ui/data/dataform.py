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
    parser.add_argument('table',type=str, help='Name of the datatable', location='query')
    parser.add_argument('id',type=str, help='Rowid', location='query')
    return parser

class DataForm(Resource):
    api=AppInfo.get_api("ui")

    @api.doc(parser=create_parser())
    def get(self, table, id):
        try:
            create_parser().parse_args()
            context=g.context

            file=f"dataforms/{table}.htm"

            fetch=build_fetchxml_by_alias(context, table, id, type="select")
            fetchparser=FetchXmlParser(fetch, context)
            rs=DatabaseServices.exec(fetchparser,context, fetch_mode=1)
            if rs.get_result()==None:
                abort(404, "Item not found => %s" % id)
            #
            # render the defined jinja template (in case ofahtm file)
            #
            logger.info(f"Redirect : {next}")

            template=JinjaTemplate.create_file_template(file)
            response = make_response(template.render({"table": table, "id": id, "data": rs.get_result()}))
            response.headers['content-type'] = 'text/html'

            return response

        except ConfigNotValid as err:
            logger.error(f"Config not valid {err}")
            return make_response(JinjaTemplate.render_status_template(500, err), 500)
        except jinja2.exceptions.TemplateNotFound as err:
            logger.info(f"TemplateNotFound: {err}")
            return make_response(JinjaTemplate.render_status_template(404, f"Template not found {err}"), 404)
        except FileNotFoundError as err:
            logger.info(f"FileNotFound: {err}")
            return make_response(JinjaTemplate.render_status_template(404, f"File not found {err}"), 404)
        except RestApiNotAllowed as err:
            logger.info(f"RestApiNotAllowed Exception: {err}")
            return redirect(f"/auth/login.htm?redirect=/{path}", code=302)
        except Exception as err:
            logger.info(f"Exception: {err}")
            return make_response(JinjaTemplate.render_status_template(500, err), 500)

def get_endpoint():
    return DataForm
