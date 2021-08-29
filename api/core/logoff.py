
import uuid
from flask import Flask,request,abort, g, session
from flask import Blueprint
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL

from core.appinfo import AppInfo
from core.database import CommandBuilderFactory as factory
from services.database import DatabaseServices
from core import log

def create_parser():
    parser=reqparse.RequestParser()
    parser.add_argument('username',type=str, help='Username', location='headers')
    parser.add_argument('password',type=str, help='Password', location='headers')
    return parser


class Logoff(Resource):
    api=AppInfo.get_api()

    @api.doc(parser=create_parser())
    def post(self):
        context=g.context
        session_id=session['session_id']

        AppInfo.logoff(context)
        session.clear()
        return {"session_id": session_id, "status":"logged_off"}

def get_endpoint():
    return Logoff


