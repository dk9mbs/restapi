
import uuid
from flask import Flask,request,abort, g, session
from flask import Blueprint
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL

from core.appinfo import AppInfo
from core.database import CommandBuilderFactory as factory
from services.database import DatabaseServices

def create_parser():
    parser=reqparse.RequestParser()
    parser.add_argument('username',type=str, help='Username', location='headers')
    parser.add_argument('password',type=str, help='Password', location='headers')
    return parser


class Login(Resource):
    api=AppInfo.get_api()

    @api.doc(parser=create_parser())
    def post(self):
        username=request.headers.get("username")
        password=request.headers.get("password")

        session_id=AppInfo.login(username, password)

        if session_id==None:
            abort(400,'Wrong username or password')
        else:
            session['session_id']=session_id
            g.context=AppInfo.create_context(session_id)
            return {"session_id": session_id, "status":"logged_on"}

class Logoff(Resource):
    api=AppInfo.get_api()

    @api.doc(parser=create_parser())
    def post(self):
        context=g.context
        session_id=session['session_id']

        AppInfo.logoff(context)
        return {"session_id": session_id, "status":"logged_off"}

def get_endpoint():
    return Login


