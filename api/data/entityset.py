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
    def get(self, table, table_view=None, related_table_alias=None, related_record_id=None):
        try:
            create_parser().parse_args()
            context=g.context
            view_meta=None
            query=""
            
            #table_view=api_table_view
            if table_view==None:
                args={}
                args['filter_field_name']=context.get_arg("filter_field_name", None)
                args['filter_value']=context.get_arg("filter_value", None)

                page=int(context.get_arg("page",0))
                page_size=int(context.get_arg("page_size", 5000))

                if related_table_alias==None:
                    fetch=build_fetchxml_lookup(context,table,0,context.get_arg("filter_field_name", None),
                        context.get_arg("filter_value",None))
                else:
                    fetch=build_fetchxml_referenced_records(context, table,0,related_record_id, related_table_alias)
                fetchparser=FetchXmlParser(fetch, context, page=page, page_size=page_size)
            else:
                query_key=f"dataformlist_query_{table}"
                operator_key=f"dataformlist_op_{table}"

                page=int(context.get_arg('page', default=0))
                #page_size=int(context.get_arg('page_size', default=0))
                page_size=int(Setting.get_value(context, "datalist.page_size","10"))

                if page<=0:
                    page=0

                query=context.get_arg('query', default=None)
                operator=context.get_arg('operator', None)

                if query==None:
                    query=context.get_session_value(query_key, None)
                else:
                    context.set_session_value(query_key, query)

                if query==None:
                    query=""

                query=query.replace("*","%")

                if operator==None:
                    operator="like"

                if operator=="like":
                    query=f"{query}%"

                table_meta=read_table_meta(context,alias=table)
                view_meta=read_table_view_meta(context, table_meta['id'], table_view, 'LISTVIEW')

                fetch=view_meta['fetch_xml']

                fetch=fetch.replace("$$query$$", query)
                fetch=fetch.replace("$$operator$$", operator)

                fetchparser=FetchXmlParser(fetch, context, page=page, page_size=page_size)

            rs=DatabaseServices.exec(fetchparser,context,fetch_mode=0)
            result=rs.get_result()
                        
            view=context.get_arg("view", None)

            if view!=None:
                # list implemented
                #file=f"templates/base/datalist.htm"
                """
                query_key=f"dataformlist_query_{table}"
                operator_key=f"dataformlist_op_{table}"

                page=int(context.get_arg('page', default=0))
                #page_size=int(context.get_arg('page_size', default=0))
                page_size=int(Setting.get_value(context, "datalist.page_size","10"))

                if page<=0:
                    page=0

                query=context.get_arg('query', default=None)
                operator=context.get_arg('operator', None)

                if query==None:
                    query=context.get_session_value(query_key, None)
                else:
                    context.set_session_value(query_key, query)

                if query==None:
                    query=""

                query=query.replace("*","%")

                if operator==None:
                    operator="like"

                if operator=="like":
                    query=f"{query}%"

                table_meta=read_table_meta(context,alias=table)
                view_meta=read_table_view_meta(context, table_meta['id'], table_view, 'LISTVIEW')

                fetch=view_meta['fetch_xml']

                fetch=fetch.replace("$$query$$", query)
                fetch=fetch.replace("$$operator$$", operator)

                fetchparser=FetchXmlParser(fetch, context, page=page, page_size=page_size)
                rs=DatabaseServices.exec(fetchparser,context,fetch_mode=0)
                """

                #template=JinjaTemplate.create_file_template(context, file)
                #response = make_response(template.render({"data": rs.get_result(),
                #            "columns": fetchparser.get_columns(),
                #            "table": table,
                #            "table_meta": table_meta,
                #            "view_meta": view_meta,
                #            "pagemode": "dataformlist",
                #            "context": context,
                #            "query": query.replace("%",""),
                #            "page": page,
                #            "page_size": page_size, "page_count": rs.get_page_count() }))
                #response.headers['content-type'] = 'text/html'
                #return response
                #
                # ****************** end list ************************
                #

                formatter=OutDataFormatter(context,view,2, table, rs)
                #table_meta set in table_info.render automaticly
                #formatter.add_template_var("table_meta", read_table_meta(context, alias=table))
                formatter.add_template_var("context", context)
                #formatter.add_template_var("table_meta", read_table_meta(context, alias=table))
                formatter.add_template_var("context", context)
                formatter.add_template_var("table", table)
                #formatter.add_template_var("pagemode", "dataforminsert")
                formatter.add_template_var("id", '')

                formatter.add_template_var("data", rs.get_result())
                #formatter.add_template_var("data", {"board_id": 1, "subject": "TEST", "msg_text":"Neues Ticket:"})


                #formatter.add_template_var("fields", fields_meta)
                #formatter.add_template_var("title",  f"{table_meta['name']} - {rs.get_result()[table_meta['desc_field_name']]}")

                # List
                formatter.add_template_var("data_columns", fetchparser.get_columns())
                formatter.add_template_var("view_meta", view_meta )
                #formatter.add_template_var("pagemode", "dataformlist" )
                formatter.add_template_var("query", query.replace("%","") )
                formatter.add_template_var("page", page)
                formatter.add_template_var("page_size", page_size)
                formatter.add_template_var("page_count", rs.get_page_count() )
                #formatter.add_template_var("table_meta", table_meta )
                # end list


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
