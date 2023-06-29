import datetime
import requests

from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices
from core import log

logger=log.create_logger(__name__)

def config():
      return {"raise_exception": False}

def execute(context, plugin_context, params):
    code=plugin_context['inline_code']

    globals = {'xxx__builtins__' : None, 'params': params}

    locals = {'print': print,
            'dir': dir,
            'context': context,
            'plugin_context': plugin_context}

    exec(code, globals, locals)
