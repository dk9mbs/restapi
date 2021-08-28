#!/usr/bin/python3

import sys
import json
import jinja2
import os
from flask import Flask, g, session
from flask import abort
from flask import Blueprint
from flask import request
from flask import make_response
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL

from core.appinfo import AppInfo
from services.fetchxml import build_fetchxml_by_alias
from services.database import DatabaseServices
from core.fetchxmlparser import FetchXmlParser
from core.jsontools import json_serial


def create_parser():
    parser=reqparse.RequestParser()
    parser.add_argument('select',type=str, help='Valid sql select', location='query')
    return parser

class Content(Resource):
    api=AppInfo.get_api()

#    @api.doc(parser=create_parser_get())
    def get(self, path):
        try:

            create_parser().parse_args()
            context=g.context


            www_root="/home/dk9mbs/src/restapi/ui/"
            #if not os.path.isfile(www_root+path):
            #    abort(404,"File not found")

            loader=jinja2.FileSystemLoader(www_root);

            jenv = jinja2.Environment(
                loader=loader,
                extensions=['jinja2.ext.autoescape'],
                autoescape=False)

            template=jenv.get_template(path)

            response = make_response(template.render())
            response.headers['content-type'] = 'text/html'

            #return  template.render(), 200, {'Content-Type': 'text/html; charset=utf-8'}
            return response

            #fetch=build_fetchxml_by_alias(context, table, id, type="select")
            #fetchparser=FetchXmlParser(fetch, context)
            #rs=DatabaseServices.exec(fetchparser,context, fetch_mode=1)
            #if rs.get_result()==None:
            #    abort(400, "Item not found => %s" % id)

            #return rs.get_result()
        except jinja2.exceptions.TemplateNotFound as err:
            print(err)
            abort(404, f"Template not found: {err}")
        except NameError as err:
            abort(400, f"{err}")
        except Exception as err:
            abort(500,f"{err}")

def get_endpoint():
    return Content
