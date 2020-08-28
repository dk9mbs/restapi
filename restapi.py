#!/usr/bin/python3

from flask import Flask, g, session, request, abort
from flask import Blueprint
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL
from config import CONFIG
from core.appinfo import AppInfo

AppInfo.init(__name__, CONFIG['default'])

# Core api endpoints
# do not import before AppInfo.init() !!!
import api.entity
import api.entitylist
import api.entityadd
import api.login

app=AppInfo.get_app()

@app.before_request
def before_request():
    g.context=None

    if request.endpoint!='login':
        if 'session_id' in session:
            g.context=AppInfo.create_context(session['session_id'])
        else:
            abort(400, 'No session_id in session!!!' )

AppInfo.get_api().add_resource(api.login.Login ,"/api/v1.0/core/login")
AppInfo.get_api().add_resource(api.login.Logoff ,"/api/v1.0/core/logoff")
AppInfo.get_api().add_resource(api.entity.get_endpoint(),"/api/v1.0/data/<table>/<id>")
AppInfo.get_api().add_resource(api.entitylist.get_endpoint(),"/api/v1.0/data/<table>")
AppInfo.get_api().add_resource(api.entityadd.get_endpoint(),"/api/v1.0/data/<table>")

@app.teardown_request
def teardown_request(error=None):
    if not g.context==None:
        AppInfo.save_context(g.context)

    if error:
        print(str(error))

if __name__ == '__main__':
    AppInfo.get_app().run(debug=True)
