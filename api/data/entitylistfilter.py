import sys
import json
from flask import Flask,request,abort,g ,session
from flask import Blueprint
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL
from datetime import date, datetime

from core.appinfo import AppInfo
from services.fetchxml import build_fetchxml_by_alias
from services.database import DatabaseServices
from core.fetchxmlparser import FetchXmlParser

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
            fetchparser=FetchXmlParser(fetch)
            rs=DatabaseServices.exec(fetchparser,context,fetch_mode=0)
            test= json.dumps(rs.get_result(), default=json_serial)
            return json.loads(test)
        except NameError as err:
            abort(400, f"{err}")
        except Exception as err:
            abort(500,f"{err}")



def get_endpoint():
    return EntityListFilter
