import datetime
import requests

from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices
from core import log

logger=log.create_logger(__name__)

def execute(context, plugin_context, params):
    code=plugin_context['inline_code']

    globals = {'__builtins__' : None}
    locals = {'print': print,
            'dir': dir,
            'context': context,
            'plugin_context': plugin_context,
            'params': params}

    exec(code, globals, locals)
