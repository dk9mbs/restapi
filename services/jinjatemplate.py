import jinja2
import os
from flask import g

from core import log
from core.plugin import Plugin
from core.appinfo import AppInfo
from core.jinjaenv import JinjaEnvironment
from services.filesystemtools import FileSystemTools

logger=log.create_logger(__name__)

class JinjaTemplate:
    @staticmethod
    def __create_environment(context, loader):
        jenv=JinjaEnvironment(context,loader)

        #jenv = jinja2.Environment(
        #    loader=loader,
        #    extensions=['jinja2.ext.autoescape'],
        #    autoescape=False)

        #jenv.globals['datacomboview'] = JinjaTemplate.__data_combo_view

        #params={"environment": jenv, "loader": loader}
        #handler=Plugin(context, "jinja_environment","create")
        #handler.execute('after', params)

        return jenv.get_environment()


    @staticmethod
    def create_file_template(context, path):
        www_root=AppInfo.get_current_config("ui","wwwroot",exception=True)
        loader=jinja2.FileSystemLoader(www_root)

        jenv=JinjaTemplate.__create_environment(context, loader)

        template=jenv.get_template(path)
        return template

    @staticmethod
    def create_string_template(context, template):
        jenv=JinjaTemplate.__create_environment(context, loader=jinja2.BaseLoader())

        template=jenv.from_string(template)
        return template

    @staticmethod
    def render_status_template(context, http_status, err_desc):
        www_root=AppInfo.get_current_config("ui","wwwroot",exception=True)

        path=f"templates/error/{http_status}.htm"
        default_template="templates/error/default.htm"

        template=None
        log.create_logger(__name__).info(f"{FileSystemTools.format_path(www_root)}{path}")

        if os.path.isfile(f"{FileSystemTools.format_path(www_root)}{path}"):
            template=JinjaTemplate.create_file_template(context, path).render({"error": http_status, "description": err_desc})
        elif os.path.isfile(f"{FileSystemTools.format_path(www_root)}{default_template}"):
            template=JinjaTemplate.create_file_template(context, default_template).render({"error": http_status, "description": err_desc})
        else:
            template=JinjaTemplate.create_string_template(context,
            """<div>Statuscode_:{{ error }}</div><div>Description:{{ description }}</div>"""
            ).render({"error": http_status, "description": err_desc})

        return template

