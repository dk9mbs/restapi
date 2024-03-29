import datetime
import requests
import json

from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices
from core import log, jsontools

from services.mqtt_client import MqttClient
from core.appinfo import AppInfo

logger=log.create_logger(__name__)

def execute(context, plugin_context, params):
    now=datetime.datetime.now()
    config=plugin_context['config']
    trigger=plugin_context['trigger']
    retain=True

    topic=_get_config_value(config, "endpoint", "restapi/$instance/core/event/$publisher/$trigger")
    filter=_get_config_value(config, "filter", '[]').replace("'", "\"")
    filter=json.loads(filter)

    if 'data' in params:
        payload=params['data']
    elif 'input' in params:
        payload=params['input']
    else:
        payload={}

    if not filter==[]:
        for i in filter:
            if not i in payload:
                return

    topic=topic.replace("$publisher", (plugin_context['publisher']).lower())
    topic=topic.replace("$trigger", (plugin_context['trigger']).lower())
    topic=topic.replace("$type", (plugin_context['type']).lower())
    topic=topic.replace("$instance", AppInfo.get_current_config("instance","id", "_"))

    if trigger.upper()=="INSERT" or trigger.upper()=="UPDATE" or trigger.upper()=="DELETE":
        for key,val in payload.items():
            topic=topic.replace(f"$value_{key}", str(val['value']))

    with MqttClient(context) as client:
        client.publish(topic, json.dumps(payload), retain=retain)

    plugin_context['response']['status_code']=200
    plugin_context['response']['payload']="OK"

def _get_config_value(config, name, default):
    if name in config:
        return config[name]

    return default
