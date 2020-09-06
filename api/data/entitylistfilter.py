#!/usr/bin/python3
import json
from flask import Flask,request,abort,g ,session
from flask import Blueprint
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL
from datetime import date, datetime

from core.appinfo import AppInfo
from core.database import CommandBuilderFactory as factory
from services.fetchxml import build_fetchxml_by_alias
from services.database import DatabaseServices

def create_parser():
    parser=reqparse.RequestParser()
    return parser

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


class EntityListFilter(Resource):
    api=AppInfo.get_api()
    @api.doc(parser=create_parser())
    def post(self):
        try:
            parser=create_parser().parse_args()
            context=g.context
            fetch=request.data
            builder=factory.create_command('select', fetch_xml=fetch)
            rs=DatabaseServices.exec(builder,context,fetch_mode=0)
            test= json.dumps(rs.get_result(), default=json_serial)
            return json.loads(test)
        except NameError as err:
            abort(400, f"{err}")



def get_endpoint():
    return EntityListFilter
