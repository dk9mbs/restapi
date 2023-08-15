#!/usr/bin/python3

import sys
import json
import traceback
from flask import Flask, g, session, make_response
from flask import abort
from flask import Blueprint
from flask import request
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL

from services.database import DatabaseServices
from core.fetchxmlparser import FetchXmlParser
from core.jsontools import json_serial
from core.plugin import Plugin
from core.appinfo import AppInfo
from core import log

logger=log.create_logger(__name__)

def create_parser_post():
    parser=reqparse.RequestParser()
    parser=reqparse.RequestParser()
    parser.add_argument('params', type=str, help='Json data',default={}, location='json')
    return parser

class Action(Resource):
    api=AppInfo.get_api()

    @api.doc(parser=create_parser_post())
    def post(self,action):
        try:
            create_parser_post().parse_args()
            context=g.context

            if request.json==None:
                abort(400, f"cannot extract json data in body action:{action}")

            params={"input": request.json, "output": {}}
            handler=Plugin(context, action, "execute")
            handler.execute('before', params)

            output=params['output']

            response = make_response(output, 200)
            return response

        except NameError  as err:
            logger.error(f"------- {err}")
            traceback.print_exc()
            abort(400, f"{err}")
        except Exception as err:
            logger.error(f"------- {err}")
            traceback.print_exc()
            abort(500,f"{err}")


def get_endpoint():
    return Action
