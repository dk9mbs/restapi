#!/usr/bin/python3
#import logging
import importlib

from flask import Flask, g, session, request, abort
from flask import Blueprint
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL
from config import CONFIG
from core.appinfo import AppInfo
from core import log

AppInfo.init(__name__, CONFIG['default'])

# Core api endpoints
# do not import before AppInfo.init() !!!
import api.data.entity
import api.data.entitylistfilter
import api.data.entityadd
import api.core.login

logger=log.create_logger(__name__)

app=AppInfo.get_app()

@app.before_request
def before_request():
    g.context=None

    if request.endpoint!='login':
        if 'session_id' in session:
            try:
                g.context=AppInfo.create_context(session['session_id'])
            except NameError as err:
                abort(400, f"{err}")
        else:
            abort(400, 'No session_id in session!!!' )

AppInfo.get_api().add_resource(api.core.login.Login ,"/api/v1.0/core/login")
AppInfo.get_api().add_resource(api.core.login.Logoff ,"/api/v1.0/core/logoff")
AppInfo.get_api().add_resource(api.data.entity.get_endpoint(),"/api/v1.0/data/<table>/<id>")
AppInfo.get_api().add_resource(api.data.entitylistfilter.get_endpoint(),"/api/v1.0/data")
AppInfo.get_api().add_resource(api.data.entityadd.get_endpoint(),"/api/v1.0/data/<table>")
#
# load the customer plugins
#
#with app.app_context():
#    print(importlib.import_module("tuxlog").register())


@app.teardown_request
def teardown_request(error=None):
    if not g.context==None:
        AppInfo.save_context(g.context)

    if error:
        print(str(error))

if __name__ == '__main__':
    logger.info(f"Port.......: {AppInfo.get_server_port()}")
    logger.info(f"Host.......: {AppInfo.get_server_host()}")
    logger.info(f"Pluginroot.: {AppInfo.get_plugin_root()}")
    AppInfo.get_app().run(debug=True, host=AppInfo.get_server_host(), port=AppInfo.get_server_port())
