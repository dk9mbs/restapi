#!/usr/bin/python3

import sys
import json
import jinja2
import os
import urllib
from urllib.parse import urlparse
from flask import Flask, g, session, redirect, abort,request,Blueprint
from flask import make_response, send_file
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL

from services.fetchxml import build_fetchxml_by_alias
from services.database import DatabaseServices
from services.httprequest import HTTPRequest
from services.filesystemtools import FileSystemTools
from services.jinjatemplate import JinjaTemplate

from core.appinfo import AppInfo
from core.fetchxmlparser import FetchXmlParser
from core.jsontools import json_serial
from core import log
from core.exceptions import RestApiNotAllowed, ConfigNotValid
from core.setting import Setting
from core.plugin import Plugin

logger=log.create_logger(__name__)

def create_parser():
    parser=reqparse.RequestParser()
    parser.add_argument('path',type=str, help='Valid filename', location='query')
    return parser

class Portal(Resource):
    api=AppInfo.get_api("portal")

    @api.doc(parser=create_parser())
    def get(self, path="index.htm", session_id=None, content_name=None):
        try:
            host=request.host

            logger.info(f"Path: {path}")
            logger.info(f"content_name: {content_name}")
            logger.info(f"host: {host}")

            create_parser().parse_args()
            context=g.context

            portal_id=self._get_portal(context, host)

            if portal_id==None:
                portal_id=Setting.get_value(context,'portal.default_portal','default')

            #
            # render the defined jinja template (in case ofahtm file)
            #
            if path.endswith('.htm'):
                next=HTTPRequest.redirect(request)
                logger.info(f"Redirect : {next}")

                fetch=build_fetchxml_by_alias(context, "api_portal", portal_id, type="select")
                fetchparser=FetchXmlParser(fetch, context)
                rs=DatabaseServices.exec(fetchparser,context, fetch_mode=1)
                if rs.get_result()==None:
                    abort(404, "Portal not found => %s" % id)

                # render the content first
                if content_name==None:
                    content_name=HTTPRequest.get_querystring_value(request, "content_name", default="home")

                content=self.__get_content(context, portal_id, content_name)
                if content==None:
                    abort(404, "Content not found => %s" % content_name)

                params={"context": context,
                        "content_name": content_name,
                        "content_id": content['id'] }



                #
                #event handling
                #
                event_params={"params": params}
                handler=Plugin(context, f"{content['name']}" ,"render_portal_content")
                handler.execute('before', event_params)
                #
                #
                #
                template=JinjaTemplate.create_string_template(context, content['content'].encode('utf-8').decode('utf-8'))
                content_str=template.render(params)
                #
                # Render the complete page
                #
                params['content']=content_str

                #
                # Build the template
                #     
                template=JinjaTemplate.create_string_template(context, rs.get_result()['template'])
                page_str=template.render(params)
                #
                # Fire the after event
                #
                event_params['content_str']=page_str
                handler.execute('after', event_params)
                page_str=event_params['content_str']

                response = make_response(page_str)
                response.headers['content-type'] = 'text/html'
                response.headers['Access-Control-Allow-Origin'] = '*'

                return response
            else:
                www_root=FileSystemTools.format_path(AppInfo.get_current_config('ui','wwwroot', exception=True))
                return send_file(f"{www_root}{path}")

        except ConfigNotValid as err:
            logger.exception(f"Config not valid {err}")
            return make_response(JinjaTemplate.render_status_template(context,500, err), 500)
        except jinja2.exceptions.TemplateNotFound as err:
            logger.exception(f"TemplateNotFound: {err}")
            return make_response(JinjaTemplate.render_status_template(context,404, f"Template not found {err}"), 404)
        except FileNotFoundError as err:
            logger.exception(f"FileNotFound: {err}")
            return make_response(JinjaTemplate.render_status_template(context,404, f"File not found {err}"), 404)
        except RestApiNotAllowed as err:
            logger.exception(f"RestApiNotAllowed Exception: {err}")
            return redirect(f"/ui/login?redirect=/{path}", code=302)
        except Exception as err:
            logger.exception(f"XXXXXXXXXXException: {err}")
            return make_response(JinjaTemplate.render_status_template(context, 500, err), 500)

    def _get_portal(self, context, host):
        o = urlparse(request.base_url)

        fetch=f"""
        <restapi type="select">
        <table name="api_portal_host" alias="ph"/>
        <filter type="and">
            <condition field="host" value="{o.hostname}" operator="="/>
        </filter>
        </restapi>
        """

        fetchparser=FetchXmlParser(fetch, context)
        rs=DatabaseServices.exec(fetchparser,context,run_as_system=True, fetch_mode=1)
        if rs.get_eof():
            return None

        return rs.get_result()['portal_id']

    def __get_content(self,context,portal_id, content_name):
        fetch=f"""
        <restapi type="select">
        <table name="api_portal_content"/>
        <filter type="and">
            <filter type="or">
                <condition field="portal_id" value="{portal_id}" operator="="/>
                <condition field="portal_id" value="default" operator="="/>
            </filter>
            <condition field="name" value="{content_name}" operator="="/>
        </filter>
        </restapi>
        """

        fetchparser=FetchXmlParser(fetch, context)
        rs_content=DatabaseServices.exec(fetchparser,context,run_as_system=True, fetch_mode=1)
        if rs_content.get_eof():
            return None

        return rs_content.get_result()

def get_endpoint():
    return Portal

