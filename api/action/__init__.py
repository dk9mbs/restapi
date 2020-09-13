#!/usr/bin/python3

import sys
import json
from flask import Flask, g, session
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

            params={"data": request.json}
            handler=Plugin(context, action, "execute")
            handler.execute('before', params)


            return params['data']
        except NameError  as err:
            abort(400, f"{err}")
        except Exception as err:
            abort(500,f"{err}")


def get_endpoint():
    return Action
