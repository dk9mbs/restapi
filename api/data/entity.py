#!/usr/bin/python3

import sys
import json
from flask import Flask, g, session
from flask import abort
from flask import Blueprint
from flask import request
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL

from core.appinfo import AppInfo
from services.fetchxml import build_fetchxml_by_alias
from services.database import DatabaseServices
from core.fetchxmlparser import FetchXmlParser
from core.jsontools import json_serial, merge
from core.exceptions import RestApiNotAllowed
from core import log
from services.outdataformatter import OutDataFormatter
from services.httpresponse import HTTPResponse

logger=log.create_logger(__name__)

def create_parser_get():
    parser=reqparse.RequestParser()
    parser.add_argument('select',type=str, help='Valid sql select', location='query')
    return parser

def create_parser_put():
    parser=reqparse.RequestParser()
    return parser

def create_parser_delete():
    parser=reqparse.RequestParser()
    return parser


class Entity(Resource):
    api=AppInfo.get_api()

    @api.doc(parser=create_parser_delete())
    def delete(self,table,id):
        try:
            create_parser_delete().parse_args()
            context=g.context
            fetch=build_fetchxml_by_alias(context,table,id, type="delete")
            fetchparser=FetchXmlParser(fetch, context)
            rs=DatabaseServices.exec(fetchparser,context, fetch_mode=0)
            result={"rows_affected": rs.get_cursor().rowcount}
            rs.close()
            return result
        except RestApiNotAllowed as err:
            abort(400, f"{err}")
        except Exception as err:
            abort(500,f"{err}")

    @api.doc(parser=create_parser_put())
    def put(self,table,id):
        try:
            create_parser_put().parse_args()
            context=g.context
            action=None

            if request.json==None:
                abort(400, "cannot extract json data in body %s %s" % (table,id))

            for key in list(request.json):
                if key.startswith("__"):
                    if key=="__action":
                        action=request.json[key]

                    del request.json[key]

            fetch=build_fetchxml_by_alias(context, table, id, request.json, type="update")
            fetchparser=FetchXmlParser(fetch, context)
            rs=DatabaseServices.exec(fetchparser,context, fetch_mode=0)
            result={"rows_affected": rs.get_cursor().rowcount}
            rs.close()
            return result
        except RestApiNotAllowed as err:
            abort(400, f"{err}")
        except Exception as err:
            abort(500,f"{err}")


    @api.doc(parser=create_parser_get())
    def get(self,table,id,field=""):
        try:
            create_parser_get().parse_args()
            context=g.context

            fetch=build_fetchxml_by_alias(context, table, id, type="select")
            fetchparser=FetchXmlParser(fetch, context)
            rs=DatabaseServices.exec(fetchparser,context, fetch_mode=1)
            if rs.get_result()==None:
                abort(400, "Item not found => %s" % id)


            if field=="":
                result=rs.get_result()
            else:
                result=rs.get_result()[field]


            view=context.get_arg("view", None)

            if not view==None:
                from core.meta import read_table_meta, read_table_field_meta

                fields_meta=read_table_field_meta(context, table_alias=table)
                table_meta=read_table_meta(context, alias=table)

                formatter=OutDataFormatter(context,view,1, table, rs)
                formatter.add_template_var("table_meta", read_table_meta(context, alias=table))
                formatter.add_template_var("context", context)
                formatter.add_template_var("table", table)
                formatter.add_template_var("pagemode", context.get_arg("__pagemode", "dataformupdate"))
                formatter.add_template_var("id", id)
                formatter.add_template_var("data", rs.get_result())
                formatter.add_template_var("fields", fields_meta)
                formatter.add_template_var("title",  f"{table_meta['name']} - {rs.get_result()[table_meta['desc_field_name']]}")

                httpresponse=HTTPResponse(formatter.render())
                httpresponse.disable_client_cache()
                httpresponse.add_header('content-type', formatter.get_mime_type())

                if formatter.get_content_disposition() != "":
                    httpresponse.add_header('Content-Disposition',f"{formatter.get_content_disposition()};filename={formatter.get_file_name()}")

                result=httpresponse.create_response()



            return result

        except RestApiNotAllowed as err:
            abort(400, f"{err}")
        except Exception as err:
            abort(500,f"{err}")

def get_endpoint():
    return Entity
