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
from core.exceptions import RestApiNotAllowed
from core import log
from services.table_info import TableInfo

logger=log.create_logger(__name__)

def create_parser():
    parser=reqparse.RequestParser()
    return parser



class EntityAdd(Resource):
    api=AppInfo.get_api()

    @api.doc(parser=create_parser())
    def post(self, table):
        try:
            context=g.context
            action=None
            
            if request.json==None:
                abort(400, "cannot extract json data in http request for insert %s" % (table))

            tab_info=TableInfo(context,table_alias=table)
            fields_meta=tab_info.fields

            for key in list(request.json):
                if key.startswith("__"):
                    if key=="__action":
                        action=request.json[key]
                    del request.json[key]
                else:
                    for field in fields_meta:
                        if not field['field_name'].startswith('_'):
                            if self._exists_field(request.json, field['field_name']):
                                if field['field_name']== key:
                                    request.json[key]=self._value(request.json[key], field['default_value'])
                                    break
                            else:
                                request.json[field['field_name']]=self._value(None, field['default_value'])

            fetch=build_fetchxml_by_alias(context,table,None, request.json, type="insert")
            fetchparser=FetchXmlParser(fetch, context)
            rs=DatabaseServices.exec(fetchparser,context, fetch_mode=0)
            result={"rows_affected": rs.get_cursor().rowcount, "inserted_id": rs.get_inserted_id()}

            return result
        except RestApiNotAllowed as err:
            logger.exception(f"{err}")
            abort(400,f"{err}")
        except Exception as err:
            logger.exception(f"{err}")
            abort(500,f"{err}")

    def _exists_field(self, fields: list, field_name: str) -> bool:
        if field_name in fields:
            return True
        else:
            return False

    def _value(self, value, default_value):
        import datetime

        if default_value==None or default_value=='':
            return value
        
        if default_value=='current_timestamp()':
            default_value=datetime.datetime.now()

        if value=='' or value==None:
            return default_value
        else:
            return value

def get_endpoint():
    return EntityAdd
