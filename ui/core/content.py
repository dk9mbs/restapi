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

from core.appinfo import AppInfo
from services.fetchxml import build_fetchxml_by_alias
from services.database import DatabaseServices
from services.httprequest import HTTPRequest
from core.fetchxmlparser import FetchXmlParser
from core.jsontools import json_serial
from core import log
from core.exceptions import RestApiNotAllowed

logger=log.create_logger(__name__)

def create_parser():
    parser=reqparse.RequestParser()
    parser.add_argument('path',type=str, help='Vilid filename', location='query')
    return parser

class Content(Resource):
    api=AppInfo.get_api("content")

    @api.doc(parser=create_parser())
    def get(self, path):
        try:
            logger.info(f"Path: {path}")

            create_parser().parse_args()
            context=g.context
            path_root=f"/{path}"
            #
            # content class
            #
            www_root="/home/dk9mbs/src/restapi/wwwroot"
            file_full_name=f"{www_root}{path_root}"
            logger.info(f"{file_full_name}")
            #
            # load the record
            #
            if path_root!='/login.htm':
                #fetch=build_fetchxml_by_alias(context, "log_logbooks", "dk9mbs", type="select")
                fetch=build_fetchxml_by_alias(context, "api_portal", "default", type="select")
                fetchparser=FetchXmlParser(fetch, context)
                rs=DatabaseServices.exec(fetchparser,context, fetch_mode=1)
                if rs.get_result()==None:
                    abort(400, "Item not found => %s" % id)
            #
            # render the defined jinja template (in case ofahtm file)
            #
            if path.endswith('.htm'):
                next=HTTPRequest.redirect(request)
                logger.info(f"Redirect : {next}")

                loader=jinja2.FileSystemLoader(www_root);

                jenv = jinja2.Environment(
                    loader=loader,
                    extensions=['jinja2.ext.autoescape'],
                    autoescape=False)

                template=jenv.get_template(path)

                response = make_response(template.render({"redirect": next}))
                response.headers['content-type'] = 'text/html'

                return response
            else:
                #logger.info("Abbruch")
                #abort(404)
                return send_file(file_full_name)

            #
            # Send file
            #

            #
            # end of content class
            #

        except jinja2.exceptions.TemplateNotFound as err:
            logger.info(f"TemplateNotFound: {err}")
            abort(404, f"Template not found: {err}")
        except RestApiNotAllowed as err:
            logger.info(f"RestApiNotAllowed Exception: {err}")
            return redirect(f"/login.htm?redirect={path_root}", code=302)
        except Exception as err:
            logger.info(f"Exception: {err}")
            abort(500,f"{err}")

def get_endpoint():
    return Content
