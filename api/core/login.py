
import uuid
import urllib
from flask import Flask,request,abort, g, session, Blueprint, make_response, redirect
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL

from core.appinfo import AppInfo
#from core.database import CommandBuilderFactory as factory
from services.database import DatabaseServices
from core import log
from services.httprequest import HTTPRequest

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

        next = HTTPRequest.redirect(request)

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

        log.create_logger(__name__).info(f"{request.accept_mimetypes}")

        if session_id==None:
            if next==None:
                abort(400,'wrong username or password')
            else:
                return redirect(f"/ui/login?redirect={next}&msg=Wrong username or password", code=302)
        else:
            session['session_id']=session_id
            g.context=AppInfo.create_context(session_id)

            if next==None:
                response = make_response({"session_id": session_id, "status":"logged_on"})
                response.headers['content-type'] = 'text/json'
                return response
            else:
                return redirect(next, code=302)


def get_endpoint():
    return Login


