import sys
import json
import decimal
import jinja2
import os
from flask import Flask,request,abort,g ,session, make_response, redirect
from flask import Blueprint
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL
from datetime import date, datetime, time, timedelta

from core.appinfo import AppInfo
from core.fetchxmlparser import FetchXmlParser
from core.jsontools import json_serial
from core.exceptions import RestApiNotAllowed, DataViewNotFound
from core import log
from core.exceptions import RestApiNotAllowed, ConfigNotValid
from core.meta import read_table_meta, read_table_view_meta
from core.setting import Setting

from services.fetchxml import build_fetchxml_by_alias
from services.database import DatabaseServices
from services.httprequest import HTTPRequest
from services.filesystemtools import FileSystemTools
from services.jinjatemplate import JinjaTemplate

logger=log.create_logger(__name__)

def create_parser():
    parser=reqparse.RequestParser()
    parser.add_argument('table',type=str, help='Alias of the datatable', location='query')
    parser.add_argument('view',type=str, help='Dataviewname', location='query')
    return parser



class EntityList(Resource):
    api=AppInfo.get_api("ui")
    @api.doc(parser=create_parser())
    def get(self, table, view="default"):

        return redirect(f"/api/v1.0/view/{table}/{view}?view=$default_ui_list&app_id={g.context.get_arg('app_id', '1')}&page={g.context.get_arg('page','0')}&query={g.context.get_arg('query', '')}&operator={g.context.get_arg('operator', '')}", code=302)


def get_endpoint():
    return EntityList
