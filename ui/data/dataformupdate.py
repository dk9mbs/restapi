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
    parser.add_argument('table',type=str, help='Alias of the datatable', location='query')
    parser.add_argument('id',type=str, help='Rowid', location='query')
    return parser

class DataFormUpdate(Resource):
    api=AppInfo.get_api("ui")

    @api.doc(parser=create_parser())
    def get(self, table, id):
        try:
            create_parser().parse_args()
            context=g.context

            file=f"templates/{table}_update.htm"

            fetch=build_fetchxml_by_alias(context, table, id, type="select")
            fetchparser=FetchXmlParser(fetch, context)
            rs=DatabaseServices.exec(fetchparser,context, fetch_mode=1)
            if rs.get_result()==None:
                abort(404, "Item not found => %s" % id)
            #
            # render the defined jinja template (in case ofahtm file)
            #
            logger.info(f"Redirect : {next}")

            template=JinjaTemplate.create_file_template(context,file)
            response = make_response(template.render({"table": table,
                    "pagemode": "dataformupdate",
                    "id": id, "data": rs.get_result()}))
            response.headers['content-type'] = 'text/html'

            return response

        except ConfigNotValid as err:
            logger.exception(f"Config not valid {err}")
            return make_response(JinjaTemplate.render_status_template(context,500, err), 500)
        except jinja2.exceptions.TemplateNotFound as err:
            logger.exception(f"TemplateNotFound: {err}")
            return make_response(JinjaTemplate.render_status_template(context,404, f"Template not found {err}"), 404)
        except FileNotFoundError as err:
            logger.exception(f"FileNotFound: {err}")
            return make_response(JinjaTemplate.render_status_template(context,404, f"File not found {err}"), 404)
        except RestApiNotAllowed as err:
            logger.exception(f"RestApiNotAllowed Exception: {err}")
            return redirect(f"/auth/login.htm?redirect=/{path}", code=302)
        except Exception as err:
            logger.exception(f"Exception: {err}")
            return make_response(JinjaTemplate.render_status_template(context, 500, err), 500)

def get_endpoint():
    return DataFormUpdate
