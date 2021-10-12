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
        try:
            parser=create_parser().parse_args()
            context=g.context

            file=f"templates/base/datalist.htm"
            query="%"
            if 'query' in request.args:
                query=f"%{request.args.get('query')}%"

            table_meta=read_table_meta(context,alias=table)
            view_meta=read_table_view_meta(context, table_meta['id'], view)

            fetch=view_meta['fetch_xml']
            columns=json.loads(view_meta['col_definition'])

            fetch=fetch.replace("$$query$$", query)

            fetchparser=FetchXmlParser(fetch, context)
            rs=DatabaseServices.exec(fetchparser,context,fetch_mode=0)

            template=JinjaTemplate.create_file_template(context, file)
            response = make_response(template.render({"data": rs.get_result(),
                        "columns": columns,"table": table, "table_meta": table_meta,"view_meta": view_meta, "pagemode": "dataformlist"}))

            response.headers['content-type'] = 'text/html'

            return response

        except ConfigNotValid as err:
            logger.error(f"Config not valid {err}")
            return make_response(JinjaTemplate.render_status_template(context,500, err), 500)
        except DataViewNotFound as err:
            logger.error(f"Dataview on api_table_view not found: {err}")
            return make_response(JinjaTemplate.render_status_template(context, 500, "Dataview not found!"), 500)
        except jinja2.exceptions.TemplateNotFound as err:
            logger.info(f"TemplateNotFound: {err}")
            return make_response(JinjaTemplate.render_status_template(context, 404, f"Template not found {err}"), 404)
        except FileNotFoundError as err:
            logger.info(f"FileNotFound: {err}")
            return make_response(JinjaTemplate.render_status_template(context, 404, f"File not found {err}"), 404)
        except RestApiNotAllowed as err:
            logger.info(f"RestApiNotAllowed Exception: {err}")
            return redirect(f"/ui/login?redirect=/ui/v1.0/data/view/{table}/default", code=302)
        except Exception as err:
            logger.info(f"Exception: {err}")
            return make_response(JinjaTemplate.render_status_template(context, 500, err), 500)



def get_endpoint():
    return EntityList
