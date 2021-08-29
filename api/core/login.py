
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


class Login(Resource):
    api=AppInfo.get_api()

    @api.doc(parser=create_parser())
    def post(self):
        username=""
        password=""
        if 'username' in request.headers:
            username=request.headers.get("username")
            password=request.headers.get("password")
        elif 'username' in request.form:
            username=request.form.get("username")
            password=request.form.get("password")
        elif 'restapi_username' in request.form:
            username=request.form.get("restapi_username")
            password=request.form.get("restapi_password")

        log.create_logger(__name__).info(f"{username} {password}")
        session_id=AppInfo.login(username, password)

        print(request.accept_mimetypes)
        if session_id==None:
            abort(400,'wrong username or password')
        else:
            session['session_id']=session_id
            g.context=AppInfo.create_context(session_id)
            return {"session_id": session_id, "status":"logged_on"}

def get_endpoint():
    return Login


