
import uuid
import urllib
import jwt
from flask import Flask,request,abort, g, session, Blueprint, make_response, redirect
from flask_restx import Resource, Api, reqparse
from flaskext.mysql import MySQL

from core.appinfo import AppInfo
from core.jwt_token import JwtToken
from core.setting import Setting
from core import log
from core.exceptions import WrongJwtTokenType
from services.database import DatabaseServices
from services.httprequest import HTTPRequest
from config import CONFIG

def create_parser():
    parser=reqparse.RequestParser()
    parser.add_argument('username',type=str, help='Username', location='headers')
    parser.add_argument('password',type=str, help='Password', location='headers')
    return parser


class Refresh(Resource):
    api=AppInfo.get_api()

    @api.doc(parser=create_parser())
    def post(self):

        if request.json==None:
            grant_type = request.form.get("grant_type")
            refresh_token = request.form.get("refresh_token")
            client_id = request.form.get("client_id")
            client_secret = request.form.get("client_secret")
        else:
            grant_type = request.json["grant_type"]
            refresh_token = request.json["refresh_token"]
            client_id = request.json["client_id"]
            client_secret = request.json["client_secret"]


        jwt_secret = CONFIG['default']['jwt']['secret']
        jwt_algorithm = CONFIG['default']['jwt']['algorithm']

        jwt_access = JwtToken(secret=jwt_secret, algorithm=jwt_algorithm, token_use="access")
        jwt_refresh = JwtToken(secret=jwt_secret, algorithm=jwt_algorithm, token_use="refresh")
        jwt_refresh.raise_error = True

        try:
            jwt_refresh.decode(refresh_token)
        except jwt.ExpiredSignatureError as e:
            abort(401, 'Refreshtoken expired')
        except jwt.exceptions.DecodeError as e:
            abort(500 ,'Refreshtoken decode error')
        except WrongJwtTokenType as e:
            abort(500, 'Wrong token_use')

        jwt_access.encode(jwt_refresh.payload['sub'], jwt_refresh.payload['sid'], 60)

        response = make_response({"status":"refreshed","session_id": jwt_refresh.payload['sid'],
            "access_token": jwt_access.token, "refresh_token": jwt_refresh.token})
        response.headers['content-type'] = 'text/json'

        return response


def get_endpoint():
    return Refresh


