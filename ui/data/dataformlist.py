import sys
import json
import decimal
import jinja2
import os
from flask import Flask,request,abort,g ,session, make_response
from flask import Blueprint
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL
from datetime import date, datetime, time, timedelta

from core.appinfo import AppInfo
from core.fetchxmlparser import FetchXmlParser
from core.jsontools import json_serial
from core.exceptions import RestApiNotAllowed
from core import log
from core.exceptions import RestApiNotAllowed, ConfigNotValid
from core.meta import read_table_meta

from services.fetchxml import build_fetchxml_by_alias
from services.database import DatabaseServices
from services.httprequest import HTTPRequest
from services.filesystemtools import FileSystemTools
from services.jinjatemplate import JinjaTemplate

logger=log.create_logger(__name__)

def create_parser():
    parser=reqparse.RequestParser()
    parser.add_argument('table',type=str, help='Alias of the datatable', location='query')
    return parser



class EntityList(Resource):
    api=AppInfo.get_api("ui")
    @api.doc(parser=create_parser())
    def get(self, table):
        try:
            parser=create_parser().parse_args()
            context=g.context

            file=f"templates/base/datalist.htm"
            query="%"
            if 'query' in request.args:
                query=f"%{request.args.get('query')}%"

            meta=read_table_meta(context,alias=table)

            fetch="""
            <restapi type="select">
                <table name="dummy"/>

                <filter type="and">
                    <condition field="name" value="$$query$$" operator=" like "/>
                </filter>

            </restapi>
            """

            columns=[{'name': 'id', 'header':'#'},
                {'name': 'name', 'header':'Name'},
                {'name': 'Port', 'header':'TCP Port'}]


            fetch=fetch.replace("$$query$$", query)

            fetchparser=FetchXmlParser(fetch, context)
            rs=DatabaseServices.exec(fetchparser,context,fetch_mode=0)

            template=JinjaTemplate.create_file_template(file)
            response = make_response(template.render({"data": rs.get_result(),
                        "columns": columns, "table_meta": meta}))

            response.headers['content-type'] = 'text/html'

            return response

        except ConfigNotValid as err:
            logger.error(f"Config not valid {err}")
            return make_response(JinjaTemplate.render_status_template(500, err), 500)
        except jinja2.exceptions.TemplateNotFound as err:
            logger.info(f"TemplateNotFound: {err}")
            return make_response(JinjaTemplate.render_status_template(404, f"Template not found {err}"), 404)
        except FileNotFoundError as err:
            logger.info(f"FileNotFound: {err}")
            return make_response(JinjaTemplate.render_status_template(404, f"File not found {err}"), 404)
        except RestApiNotAllowed as err:
            logger.info(f"RestApiNotAllowed Exception: {err}")
            return redirect(f"/auth/login.htm?redirect=/{path}", code=302)
        except Exception as err:
            logger.info(f"Exception: {err}")
            return make_response(JinjaTemplate.render_status_template(500, err), 500)



def get_endpoint():
    return EntityList
