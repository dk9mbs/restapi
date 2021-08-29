import sys
import json
import decimal
from flask import Flask,request,abort,g ,session
from flask import Blueprint
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL
from datetime import date, datetime, time, timedelta

from core.appinfo import AppInfo
from services.fetchxml import build_fetchxml_by_alias
from services.database import DatabaseServices
from core.fetchxmlparser import FetchXmlParser
from core.jsontools import json_serial
from core.exceptions import RestApiNotAllowed
from core import log

logger=log.create_logger(__name__)

def create_parser():
    parser=reqparse.RequestParser()
    return parser



class EntityListFilter(Resource):
    api=AppInfo.get_api()
    @api.doc(parser=create_parser())
    def post(self):
        try:
            parser=create_parser().parse_args()
            context=g.context
            fetch=request.data
            fetchparser=FetchXmlParser(fetch, context)
            rs=DatabaseServices.exec(fetchparser,context,fetch_mode=0)
            return rs.get_result()
        except RestApiNotAllowed as err:
            abort(400, f"{err}")
        except Exception as err:
            abort(500,f"{err}")



def get_endpoint():
    return EntityListFilter
