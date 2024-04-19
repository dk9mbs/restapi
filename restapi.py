#!/usr/bin/python3
import importlib

from flask import Flask, g, session, request, abort, make_response, redirect
from flask import Blueprint
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL
from config import CONFIG
from core.appinfo import AppInfo
from core import log
import jinjainit
from core.plugin import Plugin
from services.httprequest import HTTPRequest

AppInfo.init(__name__, CONFIG['default'])
jinjainit.init()

# Core api endpoints
# do not import before AppInfo.init() !!!
import api.data.entity
import api.data.entitylistfilter
import api.data.entityadd
import api.data.entityset
import api.data.file
import api.core.login
import api.core.logoff
import api.action
import api.form.entityupdate
import api.form.entityinsert
import api.imports.textimport

# import ui endpoints
import ui.core.portal
import ui.login
import ui.uihome
import ui.core.defaultpage

import ui.data.dataformlist
#import ui.data.dataformupdate
#import ui.data.dataforminsert

logger=log.create_logger(__name__)

app=AppInfo.get_app()

system=AppInfo.system_credentials()
session_id=AppInfo.login(system['username'],system['password'])
context=AppInfo.create_context(session_id, auto_logoff=True)
params={}
handler=Plugin(context, "$app_start","execute")
handler.execute('before', params)


@app.before_request
def before_request():
    g.context=None

    if AppInfo.get_current_config('instance','enable_swagger_doc',0)==0:
        if request.endpoint=='doc':
            abort(404, "Not enabled")

    #logger.info(f"Endpoint: {request.endpoint}")

    if request.endpoint!='api.login' and request.endpoint!='ui.login':
        login=False
        if 'session_id' in session:
            try:
                g.context=AppInfo.create_context(session['session_id'])
                login=True
            except NameError as err:
                logger.warning(f"Session_id found in session context: error raised: {err}")
                #abort(400, f"Session_id found in session context: error raised: {err}")

        if not login:
            auto_logoff=False
            username=""
            password=""

            if 'restapi_username' in request.headers:
                username=request.headers['restapi-username']
                password=request.headers['restapi-password']
            elif 'username' in request.headers:
                username=request.headers['username']
                password=request.headers['password']
            elif 'username' in request.args:
                username=request.args['username']
                password=request.args['password']
            elif 'apikey' in request.args:
                user=AppInfo.user_credentials_by_apikey( request.args['apikey'])
                username=user['username']
                password=user['password']
            else:
                #do not set session['session_id'] because the
                #guest session will be automaticly deactivated.
                auto_logoff=True
                guest=AppInfo.guest_credentials()
                username=guest['username']
                password=guest['password']

            session_id=AppInfo.login(username,password)
            if session_id==None:
                print(f"try to login with username: {username}")
                abort(400,'Wrong username or password')

            if not auto_logoff:
                logger.info(f"save session_id {session_id}")
                session['session_id']=session_id

            #g.context=AppInfo.create_context(session_id, auto_logoff=True)
            g.context=AppInfo.create_context(session_id, auto_logoff=auto_logoff)

        token=None
        command=None
        if 'api_token' in request.args and 'api_cmd' in request.args:
            token=request.args['api_token']
            command=request.args['api_cmd']

        if not HTTPRequest.process_command(request,request.args, g.context, token, command):
            # only when not restore, next_page
            for arg in request.args:
                g.context.set_arg(arg, request.args[arg])


AppInfo.get_api().add_resource(api.core.login.get_endpoint() ,"/v1.0/core/login")
AppInfo.get_api().add_resource(api.core.logoff.get_endpoint() ,"/v1.0/core/logoff")
AppInfo.get_api().add_resource(api.data.entity.get_endpoint(),"/v1.0/data/<table>/<id>", methods=['GET','PUT','DELETE'])
AppInfo.get_api().add_resource(api.data.entity.get_endpoint(),"/v1.0/data/<table>/<id>/<field>", methods=['GET'])
AppInfo.get_api().add_resource(api.data.entitylistfilter.get_endpoint(),"/v1.0/data", methods=['POST'])
AppInfo.get_api().add_resource(api.data.entityadd.get_endpoint(),"/v1.0/data/<table>", methods=['POST'])
AppInfo.get_api().add_resource(api.data.entityset.get_endpoint(),"/v1.0/data/<table>", methods=['GET'])
AppInfo.get_api().add_resource(api.data.entityset.get_endpoint(), "/v1.0/view/<table>/<table_view>", methods=['GET'])

# file handling
AppInfo.get_api().add_resource(api.data.file.get_endpoint(), "/v1.0/file/<path:path>", methods=['POST','GET','PUT'])
AppInfo.get_api().add_resource(api.data.file.get_endpoint(), "/v1.0/file", methods=['POST','PUT'])

# Textfile import like xml, json, csv ...
AppInfo.get_api().add_resource(api.imports.textimport.get_endpoint(), "/v1.0/import/<format>", methods=['POST'])
AppInfo.get_api().add_resource(api.imports.textimport.get_endpoint(), "/v1.0/import", methods=['POST'])

# user defined actions
AppInfo.get_api().add_resource(api.action.get_endpoint(), "/v1.0/action/<action>")

# html form updates
AppInfo.get_api().add_resource(api.form.entityupdate.get_endpoint(), "/v1.0/form/<table>/<id>", methods=['POST'])
AppInfo.get_api().add_resource(api.form.entityinsert.get_endpoint(), "/v1.0/form/<table>", methods=['POST'])

# get the dataform form edit records
#AppInfo.get_api("ui").add_resource(ui.data.dataformupdate.get_endpoint(), "/v1.0/data/<table>/<id>", methods=['GET'])
#AppInfo.get_api("ui").add_resource(ui.data.dataforminsert.get_endpoint(), "/v1.0/data/<table>", methods=['GET'])
#AppInfo.get_api("ui").add_resource(ui.data.dataformlist.get_endpoint(), "/v1.0/data/view/<table>", methods=['GET'])
AppInfo.get_api("ui").add_resource(ui.data.dataformlist.get_endpoint(), "/v1.0/data/view/<table>/<view>", methods=['GET'])
#
# login process
#
AppInfo.get_api("ui").add_resource(ui.login.get_endpoint(), "/login", methods=['GET'])
AppInfo.get_api("ui").add_resource(ui.uihome.get_endpoint(), "/home", methods=['GET'])
#
# endpoint for static and dynamic portal content
#
AppInfo.get_api("portal").add_resource(ui.core.defaultpage.get_endpoint(), "/")
AppInfo.get_api("portal").add_resource(ui.core.portal.get_endpoint(), "/VPages/<session_id>/<content_name>")
AppInfo.get_api("portal").add_resource(ui.core.portal.get_endpoint(), "/<path:path>")

logger.info(AppInfo.get_app().url_map)

params={}
handler=Plugin(context, "$app_start","execute")
handler.execute('after', params)
AppInfo.logoff(context)
context.close()

@app.teardown_request
def teardown_request(error=None):

    if not g.context==None:
        if g.context.get_auto_logoff():
            AppInfo.logoff(g.context)
            g.context.close()
        else:
            AppInfo.save_context(g.context)

    if error:
        print(str(error))


if __name__ == '__main__':
    logger.info(f"Port.......: {AppInfo.get_server_port()}")
    logger.info(f"Host.......: {AppInfo.get_server_host()}")
    logger.info(f"Pluginroot.: {AppInfo.get_plugin_root()}")
    AppInfo.get_app().run(debug=True, host=AppInfo.get_server_host(), port=AppInfo.get_server_port())
