import jinja2
import os
from flask import g

from core import log
from core.plugin import Plugin
from core.appinfo import AppInfo
from services.filesystemtools import FileSystemTools

logger=log.create_logger(__name__)

class JinjaEnvironment:
    _template_functions={}
    _filters={}

    def __init__(self, context, loader):
        self._context=context
        self._loader=loader
        self._environment=self._create_environment(context,loader)

    def get_environment(self):
        return self._environment

    def _create_environment(self,context, loader):

        jenv = jinja2.Environment(
            loader=loader,
            extensions=['jinja2.ext.autoescape'],
            autoescape=False)

        for key, fn in JinjaEnvironment._template_functions.items():
            jenv.globals[key]=fn

        for key,fn in JinjaEnvironment._filters.items():
            jenv.filters[key]=fn


        params={"environment": jenv, "loader": loader}
        handler=Plugin(context, "jinja_environment","create")
        handler.execute('after', params)

        return jenv

    @classmethod
    def register_template_function(cls, alias, fn):
        cls._template_functions[alias]=fn

    @classmethod
    def register_filter_function(cls, alias, fn):
        cls._filters[alias]=fn

    @staticmethod
    def __data_combo_view():
        return '[{"id":1,"name":"FT817"},{"id":2, "name": "IC735"}]'

