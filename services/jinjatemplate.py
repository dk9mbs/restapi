import jinja2
import os

from core import log
from core.appinfo import AppInfo
from services.filesystemtools import FileSystemTools

class JinjaTemplate:
    @staticmethod
    def create_file_template(path):
        www_root=AppInfo.get_current_config("ui","wwwroot",exception=True)

        loader=jinja2.FileSystemLoader(www_root)

        jenv = jinja2.Environment(
            loader=loader,
            extensions=['jinja2.ext.autoescape'],
            autoescape=False)

        template=jenv.get_template(path)
        return template

    @staticmethod
    def create_string_template(template):
        template = jinja2.Template(template)
        return template

    @staticmethod
    def render_status_template(http_status, err_desc):
        www_root=AppInfo.get_current_config("ui","wwwroot",exception=True)

        path=f"templates/error/{http_status}.htm"
        default_template="templates/error/default.htm"

        template=None
        log.create_logger(__name__).info(f"{FileSystemTools.format_path(www_root)}{path}")

        if os.path.isfile(f"{FileSystemTools.format_path(www_root)}{path}"):
            template=JinjaTemplate.create_file_template(path).render({"error": http_status, "description": err_desc})
        elif os.path.isfile(f"{FileSystemTools.format_path(www_root)}{default_template}"):
            template=JinjaTemplate.create_file_template(default_template).render({"error": http_status, "description": err_desc})
        else:
            template=JinjaTemplate.create_string_template(
            """<div>Statuscode:{{ error }}</div><div>Description:{{ description }}</div>"""
            ).render({"error": http_status, "description": err_desc})

        return template

