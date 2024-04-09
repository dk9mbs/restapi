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
from services.table_info import TableInfo

from core.appinfo import AppInfo
from core.fetchxmlparser import FetchXmlParser
from core.jsontools import json_serial, merge
from core import log
from core.exceptions import RestApiNotAllowed, ConfigNotValid
from core.meta import read_table_meta, read_table_field_meta
from core.permission import Permission


logger=log.create_logger(__name__)

def create_parser():
    parser=reqparse.RequestParser()
    parser.add_argument('table',type=str, help='Name of the datatable', location='query')
    return parser

class DataFormInsert(Resource):
    api=AppInfo.get_api("ui")

    @api.doc(parser=create_parser())
    def get(self, table):
        try:
            create_parser().parse_args()
            context=g.context
            data={}

            table_info=TableInfo(context, table_alias=table)

            if not Permission().validate(context, "create", context.get_username(), table_info.table_alias):
                raise RestApiNotAllowed("")

            table_meta=table_info.table_meta_data
            fields_meta=table_info.fields
            #solution_id=table_info.solution_id

            for field in fields_meta:
                json1=json.loads(field['control_config'])
                json2=json.loads(field['overwrite_control_config'])
                cfg=merge(json1, json2)
                field['control_config']=cfg
                if "default_value" in cfg:
                    data[field['name']]=cfg['default_value']

                if not context.get_arg(f"param_{field['name']}", None)==None:
                    data[field['name']]=context.get_arg(f"param_{field['name']}", None)

            if table_info.solution_id==1:
                file=f"templates/{table_info.table_alias}_insert.htm"
            else:
                file=f"solutions/{table_info.solution_id}/{table_info.table_alias}_insert.htm"
            file=f"templates/base/dataform.htm"

            template=JinjaTemplate.create_file_template(context,file)
            response = make_response(template.render({"table": table_info.table_alias,
                    "pagemode": "dataforminsert",
                    "id": "", "data": data, "context": context, "fields": fields_meta,
                    "table_meta": table_meta,
                    "title": f"{table_meta['name']} - new record"  }))

            response.headers['content-type'] = 'text/html'

            return response

        except ConfigNotValid as err:
            logger.exception(f"Config not valid {err}")
            return make_response(JinjaTemplate.render_status_template(context, 500, err), 500)
        except jinja2.exceptions.TemplateNotFound as err:
            logger.exception(f"TemplateNotFound: {err}")
            return make_response(JinjaTemplate.render_status_template(context, 404, f"Template not found {err}"), 404)
        except FileNotFoundError as err:
            logger.exception(f"FileNotFound: {err}")
            return make_response(JinjaTemplate.render_status_template(context, 404, f"File not found {err}"), 404)
        except RestApiNotAllowed as err:
            logger.exception(f"RestApiNotAllowed Exception: {err}")
            #return redirect(f"/ui/login?redirect=/ui/v1.0/data/{table}", code=302)
            return redirect(f"/ui/login?redirect={request.url}", code=302)
        except Exception as err:
            logger.exception(f"Exception: {err}")
            return make_response(JinjaTemplate.render_status_template(context, 500, err), 500)

def get_endpoint():
    return DataFormInsert
