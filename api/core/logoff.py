
import uuid
from flask import Flask,request,abort, g, session, make_response, redirect
from flask import Blueprint
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL

from core.appinfo import AppInfo
from core.database import CommandBuilderFactory as factory
from services.database import DatabaseServices
from services.httprequest import HTTPRequest
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

        session_id=''

        if 'session_id' in session:
            session_id=session['session_id']

        AppInfo.logoff(context)
        session.clear()

        next = HTTPRequest.redirect(request)

        if next==None:
            response = make_response({"session_id": session_id, "status":"logged_off"})
            response.headers['content-type'] = 'text/json'
            return response
        else:
            return redirect(next, code=302)

def get_endpoint():
    return Logoff


