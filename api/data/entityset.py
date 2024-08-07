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
from core.setting import Setting
from core.meta import read_table_view_meta, read_table_meta

from services.fetchxml import build_fetchxml_by_alias, build_fetchxml_lookup, build_fetchxml_referenced_records
from services.database import DatabaseServices
from services.outdataformatter import OutDataFormatter
from services.httpresponse import HTTPResponse
from services.jinjatemplate import JinjaTemplate

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
    def get(self, table, table_view=None, related_table_alias=None, related_record_id=None, api_version="v1.0"):
        return self._get_or_post(table=table, table_view=table_view, related_table_alias=related_table_alias, related_record_id=related_record_id, post_data=None, api_version=api_version)
    
    @api.doc(parser=create_parser())
    def post(self, table, table_view=None, related_table_alias=None, related_record_id=None, api_version="v1.0"):
        return self._get_or_post(table=table, table_view=table_view, related_table_alias=related_table_alias, related_record_id=related_record_id, post_data=request.data, api_version=api_version)

    def _get_or_post(self, table, table_view=None, related_table_alias=None, related_record_id=None, post_data=None, api_version="v1.0"):
        try:
            create_parser().parse_args()
            context=g.context
            view_meta=None
            query=""
            table_meta=read_table_meta(context,alias=table)

            if table_view==None:
                # build a normal table query or a related query
                args={}
                args['filter_field_name']=context.get_arg("filter_field_name", None)
                args['filter_value']=context.get_arg("filter_value", None)

                page=int(context.get_arg("page",0))
                page_size=int(context.get_arg("page_size", 5000))

                if related_table_alias==None and post_data==None:
                    # normal 
                    fetch=build_fetchxml_lookup(context,table,0,context.get_arg("filter_field_name", None),
                        context.get_arg("filter_value",None))
                elif post_data!=None:
                    # search with fetchxml
                    import xml.etree.ElementTree as ET
                    tree=ET.fromstring(post_data)

                    for node in tree.findall("./table"):
                        tree.remove(node)

                    node=ET.SubElement(tree,"table", {"name": table})
                    tree.append(node)
                    fetch=ET.tostring(tree)
                else:
                    fetch=build_fetchxml_referenced_records(context, table,0,related_record_id, related_table_alias)

                fetchparser=FetchXmlParser(fetch, context, page=page, page_size=page_size)
            else:
                #use a saved table_view query from api_table_view
                query_key=f"dataformlist_query_{table}"
                operator_key=f"dataformlist_op_{table}"

                page=int(context.get_arg('page', default=0))
                #page_size=int(context.get_arg('page_size', default=0))
                page_size=int(Setting.get_value(context, "datalist.page_size","10"))

                if page<=0:
                    page=0

                query=context.get_arg('query', default=None)
                operator=context.get_arg('operator', None)
                if query=='':
                    query=None

                if operator=='':
                    operator=None

                if query==None:
                    query=context.get_session_value(query_key, None)
                else:
                    context.set_session_value(query_key, query)

                if query==None or query=='':
                    query="%"

                query=query.replace("*","%")

                if operator==None:
                    operator="like"

                if operator=="like":
                    query=f"{query}%"

                #table_meta=read_table_meta(context,alias=table)
                view_meta=read_table_view_meta(context, table_meta['id'], table_view, 'LISTVIEW')

                fetch=view_meta['fetch_xml']

                fetch=fetch.replace("$$query$$", query)
                fetch=fetch.replace("$$operator$$", operator)
                print(fetch)
                fetchparser=FetchXmlParser(fetch, context, page=page, page_size=page_size)

            rs=DatabaseServices.exec(fetchparser,context,fetch_mode=0)
            result=rs.get_result()
            if api_version=="v1.1":
                result={"data": result}

            view=context.get_arg("view", None)

            if view!=None:
                # list implemented
                #file=f"templates/base/datalist.htm"
                main_record_id=context.get_arg("main_record_id", None)
                main_table_id=context.get_arg("main_table_id", None)

                data=rs.get_result()
                if main_record_id!=None and main_table_id!=None:
                    from core.meta import create_table_relation
                    data=create_table_relation(context, main_table_id, table_meta['id'],main_record_id_int=main_record_id)

                formatter=OutDataFormatter(context,view,2, table, rs)
                formatter.add_template_var("table_meta", read_table_meta(context, alias=table))
                formatter.add_template_var("context", context)
                formatter.add_template_var("context", context)
                formatter.add_template_var("table", table)
                formatter.add_template_var("id", '')
                formatter.add_template_var("data", data)
                formatter.add_template_var("data_columns", fetchparser.get_columns())
                formatter.add_template_var("view_meta", view_meta )
                formatter.add_template_var("query", query.replace("%","") )
                formatter.add_template_var("page", page)
                formatter.add_template_var("page_size", page_size)
                formatter.add_template_var("page_count", rs.get_page_count() )

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
