import datetime
import requests

from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices
from core import log

logger=log.create_logger(__name__)

def execute(context, plugin_context, params):
    now=datetime.datetime.now()
    config=plugin_context['config']

    url=__get_config_value(config, "endpoint", "http://localhost:1880/restapi/$publisher/$trigger")
    timeout=int(__get_config_value(config, "timeout", "90"))

    if 'data' in params:
        payload=params['data']
    elif 'input' in params:
        payload=params['input']
    else:
        payload={}

    payload={"payload": payload,
        "plugin_context": plugin_context}

    url=url.replace("$publisher", plugin_context['publisher'])
    url=url.replace("$trigger", plugin_context['trigger'])
    url=url.replace("$type", plugin_context['type'])

    r = requests.post(url, json=payload, timeout=timeout)

    plugin_context['response']['status_code']=r.status_code
    plugin_context['response']['payload']=r.text

def __get_config_value(config, name, default):
    if name in config:
        return config[name]

    return default
