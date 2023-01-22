#!/usr/bin/python3

import sys
import json
from flask import Flask, g, session, make_response
from flask import request, redirect, abort
from flask_restplus import Resource, Api, reqparse

from core.appinfo import AppInfo
from services.fetchxml import build_fetchxml_by_alias
from services.database import DatabaseServices
from services.httprequest import HTTPRequest

from core.fetchxmlparser import FetchXmlParser
from core.jsontools import json_serial
from core.exceptions import RestApiNotAllowed
from core import log
from core.file import File
from core.plugin import Plugin
from core.file_system_tools import get_file_content

logger=log.create_logger(__name__)

def create_parser_post():
    parser=reqparse.RequestParser()
    parser.add_argument('format',type=str, help='format alias', location='url')
    return parser

class TextImport(Resource):
    api=AppInfo.get_api()

    @api.doc(parser=create_parser_post())
    def post(self, format=None):
        try:
            context=g.context
            connection=context.get_connection()

            if format==None:
                format=request.form['type_id']

            logger.info(f"Format detected: {format}")
            next = HTTPRequest.redirect(request)

            for f in request.files.getlist('file'):
                import os
                import uuid
                from werkzeug.utils import secure_filename
                from core.setting import Setting

                filename = secure_filename(f"restapi_{uuid.uuid4()}-{f.filename}")
                path=Setting.get_value(context, 'upload.file.path', '/tmp/')
                file_full_name=os.path.join(path, filename)
                f.save(file_full_name)

                plugin=Plugin(context, f"textfileimport2_{format}", "post")
                plugin.execute("before", {"data": {"file_full_name": file_full_name}})
                plugin.execute("after", {"data": {"file_full_name": file_full_name}})

                #deprecated!!!
                content=get_file_content(file_full_name)
                plugin=Plugin(context, f"textfileimport_{format}", "post")
                plugin.execute("before", {"data": {"content": content}})
                plugin.execute("after", {"data": {"content": content}})

            if next==None:
                return make_response(dict({"results": "" ,"status":"ok"}) ,200)
            else:
                return redirect(next, code=302)

        except RestApiNotAllowed as err:
            abort(400, f"{err}")
        except Exception as err:
            abort(500,f"{err}")

def get_endpoint():
    return TextImport
