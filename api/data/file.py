#!/usr/bin/python3
import sys
import json
from flask import Flask,request,abort, g, session, redirect, make_response
from flask import Blueprint
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL
from datetime import date, datetime

from core.appinfo import AppInfo
from core.fetchxmlparser import FetchXmlParser
from core.jsontools import json_serial
from core.exceptions import RestApiNotAllowed
from core import log
from core.meta import read_table_meta
from core.exceptions import TableMetaDataNotFound, FileNotFoundInDatabase
from core.file import File

from services.httprequest import HTTPRequest
from services.fetchxml import build_fetchxml_by_alias
from services.database import DatabaseServices
from services.jinjatemplate import JinjaTemplate

logger=log.create_logger(__name__)

def create_parser():
    parser=reqparse.RequestParser()
    return parser


class PostFile(Resource):
    api=AppInfo.get_api()

    @api.doc(parser=create_parser())
    def get(self, path):
        try:
            context=g.context
            connection=context.get_connection()

            file=File()
            result=file.read_file(context, path)
            mode=result['mode']

            if result==None:
                return make_response({"status": "Err","error": f"File not found: {path}" }, 404)

            response = make_response(result[mode])

            response.headers.set('Content-Type', result['mime_type'])
            #response.headers.set('Content-Disposition', 'attachment', filename='test.jpg')
            response.headers.set('Content-Disposition', 'inline', filename=result['name'])
            return response

        except Exception as err:
            logger.exception(f"Exception: {err}")
            return make_response({"status": "Err","error": str(err) }, 500)


    @api.doc(parser=create_parser())
    def post(self, path):
        try:
            context=g.context
            connection=context.get_connection()
            result=[]

            for f in request.files.getlist('file'):
                file=File()
                file.create_file(context, f, path)
                result.append({"status": "OK","file_id": file.get_file_id(), "remote_path": path })

            return make_response(dict({"results": result,"status":"ok"}) ,200)

        except Exception as err:
            logger.exception(f"Exception: {err}")
            return make_response({"status": "Err","error": str(err) }, 500)


    @api.doc(parser=create_parser())
    def put(self, path):
        try:
            context=g.context
            connection=context.get_connection()
            result=[]
            for f in request.files.getlist('file'):
                file=File()
                file.update_file(context, f, path)
                result.append({"status": "OK","file_id": file.get_file_id(), "remote_path": path })

            return make_response(dict({"results": result,"status":"ok"}) ,200)

        except FileNotFoundInDatabase as err:
            logger.exception(f"FileNotFoundInDatabase: {err}")
            return make_response({"status": "Err","error": str(err) }, 404)
        except Exception as err:
            logger.exception(f"Exception: {err}")
            return make_response({"status": "Err","error": str(err) }, 500)

def get_endpoint():
    return PostFile
