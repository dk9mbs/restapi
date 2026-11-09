#!/usr/bin/python3
import sys
import json
import uuid
from flask import Flask,request,abort, g, session
from flask import Blueprint
from flask_restx import Resource, Api, reqparse
from flaskext.mysql import MySQL
from datetime import date, datetime
from werkzeug.exceptions import HTTPException

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
            client_sys_row_id=None

            if request.json==None:
                abort(400, "cannot extract json data in http request for insert %s" % (table))

            tab_info=TableInfo(context,table_alias=table)
            fields_meta=tab_info.fields

            for key in list(request.json):
                if key.startswith("__"):
                    if key=="__action":
                        action=request.json[key]
                    elif key=="__sys_row_id":
                        client_sys_row_id=self._validate_uuid(request.json[key])
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

            # do not use the uuid() function as an string default value
            if 'sys_row_id' in request.json:
                del request.json['sys_row_id']

            # client supplied a deterministic sys_row_id (idempotent insert)
            if client_sys_row_id is not None:
                request.json['sys_row_id']=client_sys_row_id

            fetch=build_fetchxml_by_alias(context,table,None, request.json, type="insert")
            fetchparser=FetchXmlParser(fetch, context)
            rs=DatabaseServices.exec(fetchparser,context, fetch_mode=0)
            result={"rows_affected": rs.get_cursor().rowcount, "inserted_id": rs.get_inserted_id()}

            return result
        except HTTPException:
            # let abort(...) pass through with its original status code
            raise
        except RestApiNotAllowed as err:
            logger.exception(f"{err}")
            abort(400,f"{err}")
        except Exception as err:
            # MySQL error 1062: duplicate key -> record already exists
            if self._is_duplicate_key(err):
                logger.warning(f"duplicate insert into {table}: {err}")
                abort(409,f"{err}")
            logger.exception(f"{err}")
            abort(500,f"{err}")

    def _validate_uuid(self, value) -> str:
        try:
            return str(uuid.UUID(str(value)))
        except (ValueError, TypeError):
            abort(400, f"__sys_row_id is not a valid uuid: {value}")

    def _is_duplicate_key(self, err: Exception) -> bool:
        while err is not None:
            args=getattr(err, "args", None)
            if args and args[0]==1062:
                return True
            err=err.__cause__ or err.__context__
        return False

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

