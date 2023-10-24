#!/usr/bin/python3
import sys
import json
import datetime
from flask import Flask,request,abort, g, session, make_response, Blueprint
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL
from datetime import date, datetime

from core.appinfo import AppInfo
from core.fetchxmlparser import FetchXmlParser
from core.jsontools import json_serial
from core.exceptions import RestApiNotAllowed
from core import log

from services.fetchxml import build_fetchxml_by_alias, build_fetchxml_lookup
from services.database import DatabaseServices
from services.outdataformatter import OutDataFormatter
from services.httpresponse import HTTPResponse

logger=log.create_logger(__name__)

def create_parser():
    parser=reqparse.RequestParser()
    parser.add_argument('table',type=str, help='Tablename', location='query')
    #parser.add_argument('where',type=str, help='Valid sql where clause', location='query')
    #parser.add_argument('orderby',type=str, help='Valid sql orderby clause', location='query')
    #parser.add_argument('select',type=str, help='Valid sql select', location='query')
    #parser.add_argument('pagesize', type=int, help='Pagesize of the resultset',default=5000, location='query')
    #parser.add_argument('page', type=int, help='Page',default=1, location='query')
    return parser



class EntitySet(Resource):
    api=AppInfo.get_api()

    api=AppInfo.get_api()
    @api.doc(parser=create_parser())
    def get(self, table):
        try:
            create_parser().parse_args()
            context=g.context
            args={}
            args['filter_field_name']=context.get_arg("filter_field_name", None)
            args['filter_value']=context.get_arg("filter_value", None)

            page=int(context.get_arg("page",0))
            page_size=int(context.get_arg("page_size", 5000))

            fetch=build_fetchxml_lookup(context,table,0,context.get_arg("filter_field_name", None),
                context.get_arg("filter_value",None),fields_select=['id'])
            fetchparser=FetchXmlParser(fetch, context, page=page, page_size=page_size)
            rs=DatabaseServices.exec(fetchparser,context,fetch_mode=0)
            result=rs.get_result()

            view=context.get_arg("view", None)

            if not view==None:
                from core.meta import read_table_meta

                formatter=OutDataFormatter(context,view,2, table, rs)
                formatter.add_template_var("table_meta", read_table_meta(context, alias=table))
                formatter.add_template_var("context", context)

                httpresponse=HTTPResponse(formatter.render())
                httpresponse.disable_client_cache()
                httpresponse.add_header('content-type', formatter.get_mime_type())

                if formatter.get_content_disposition() != "":
                    httpresponse.add_header('Content-Disposition',f"{formatter.get_content_disposition()};filename={formatter.get_file_name()}")

                result=httpresponse.create_response()


            return result
        except RestApiNotAllowed as err:
            logger.info(f"{err}")
            abort(400, f"{err}")
        except Exception as err:
            abort(500,f"{err}")

def get_endpoint():
    return EntitySet
