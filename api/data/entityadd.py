#!/usr/bin/python3
import sys
import json
from flask import Flask,request,abort, g, session
from flask import Blueprint
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL
from datetime import date, datetime

from core.appinfo import AppInfo
from services.fetchxml import build_fetchxml_by_alias
from services.database import DatabaseServices
from core.fetchxmlparser import FetchXmlParser
from core.jsontools import json_serial

def create_parser():
    parser=reqparse.RequestParser()
    parser.add_argument('where',type=str, help='Valid sql where clause', location='query')
    parser.add_argument('orderby',type=str, help='Valid sql orderby clause', location='query')
    parser.add_argument('select',type=str, help='Valid sql select', location='query')
    parser.add_argument('pagesize', type=int, help='Pagesize of the resultset',default=5000, location='query')
    parser.add_argument('page', type=int, help='Page',default=1, location='query')
    return parser



class EntityAdd(Resource):
    api=AppInfo.get_api()

    api=AppInfo.get_api()
    @api.doc(parser=create_parser())
    def get(self, table):
        try:
            create_parser().parse_args()
            context=g.context
            fetch=build_fetchxml_by_alias(context,table,None, None,type="select")
            fetchparser=FetchXmlParser(fetch)
            rs=DatabaseServices.exec(fetchparser,context,fetch_mode=0)
            return rs.get_result()
        except NameError as err:
            print(err)
            abort(400, f"{err}")
        except Exception as err:
            abort(500,f"{err}")

    @api.doc(parser=create_parser())
    def post(self, table):
        try:
            context=g.context

            if request.json==None:
                abort(400, "cannot extract json data in http request for insert %s" % (table))

            fetch=build_fetchxml_by_alias(context,table,None, request.json, type="insert")
            fetchparser=FetchXmlParser(fetch)
            rs=DatabaseServices.exec(fetchparser,context, fetch_mode=0)
            result={"rows_affected": rs.get_cursor().rowcount}

            return result
        except NameError as err:
            abort(400,f"{err}")
        except Exception as err:
            abort(500,f"{err}")

def get_endpoint():
    return EntityAdd
