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
import api.core.logoff
import api.action
# import ui endpoints
import ui.core.content

logger=log.create_logger(__name__)

app=AppInfo.get_app()
#
# create blueprints
#
bp_api=Blueprint('api', __name__)
bp_ui=Blueprint('ui', __name__)
bp_content=Blueprint('content',__name__)

ui_mod=Api(bp_ui)
api_mod=Api(bp_api)
content_mod=Api(bp_content)

app.register_blueprint(bp_ui, url_prefix='/ui')
app.register_blueprint(bp_api, url_prefix='/api')
app.register_blueprint(bp_content)

@app.before_request
def before_request():
    g.context=None

    if AppInfo.get_current_config('instance','enable_swagger_doc',0)==0:
        if request.endpoint=='doc':
            abort(404, "Not enabled")

    if request.endpoint!='login':
        if 'session_id' in session:
            try:
                g.context=AppInfo.create_context(session['session_id'])
            except NameError as err:
                abort(400, f"Session_id found in session context: error raised: {err}")
                pass
        else:
            #do not set session['session_id'] because the
            #guest session will be automaticly deactivated.
            username=""
            password=""
            if 'restapi_username' in request.headers:
                username=request.headers['restapi-username']
                password=request.headers['restapi-password']
            elif 'username' in request.headers:
                username=request.headers['username']
                password=request.headers['password']
            else:
                guest=AppInfo.guest_credentials()
                username=guest['username']
                password=guest['password']

            session_id=AppInfo.login(username,password)
            if session_id==None:
                print(f"try to login with username: {username}")
                abort(400,'Wrong username or password')

            g.context=AppInfo.create_context(session_id, auto_logoff=True)


api_mod.add_resource(api.core.login.get_endpoint() ,"/v1.0/core/login")
api_mod.add_resource(api.core.logoff.get_endpoint() ,"/v1.0/core/logoff")
api_mod.add_resource(api.data.entity.get_endpoint(),"/v1.0/data/<table>/<id>")
api_mod.add_resource(api.data.entitylistfilter.get_endpoint(),"/v1.0/data")
api_mod.add_resource(api.data.entityadd.get_endpoint(),"/v1.0/data/<table>")
api_mod.add_resource(api.action.get_endpoint(), "/v1.0/action/<action>")
#
# UI endpoints
#
#ui_mod.add_resource(ui.core.login.get_endpoint(), "/v1.0/core/login")
#
# endpoint for static and dynamics content
#
content_mod.add_resource(ui.core.content.get_endpoint(), "/<path:path>")

logger.info(AppInfo.get_app().url_map)

@app.teardown_request
def teardown_request(error=None):

    if not g.context==None:
        if g.context.get_auto_logoff():
            AppInfo.logoff(g.context)
        else:
            AppInfo.save_context(g.context)

    if error:
        print(str(error))


if __name__ == '__main__':
    logger.info(f"Port.......: {AppInfo.get_server_port()}")
    logger.info(f"Host.......: {AppInfo.get_server_host()}")
    logger.info(f"Pluginroot.: {AppInfo.get_plugin_root()}")
    AppInfo.get_app().run(debug=True, host=AppInfo.get_server_host(), port=AppInfo.get_server_port())
