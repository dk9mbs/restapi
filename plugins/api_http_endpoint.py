import datetime
import requests

from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices
from core import log

logger=log.create_logger(__name__)

def execute(context, plugin_context, params):
    now=datetime.datetime.now()
    timeout=90
    url="http://localhost:1880/test/$publisher/$trigger"

    if 'data' in params:
        payload=params['data']
    elif 'input' in params:
        payload=params['input']
    else:
        payload={}

    payload={"payload": payload,
        "plugin_context": plugin_context,
        "session_id": context.get_session_id()}

    url=url.replace("$publisher", plugin_context['publisher'])
    url=url.replace("$trigger", plugin_context['trigger'])
    url=url.replace("$type", plugin_context['type'])

    r = requests.post(url, json=payload, timeout=timeout)

    params['response']['status_code']=r.status_code
    params['response']['payload']=r.text

