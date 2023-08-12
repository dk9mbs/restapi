import json
import paho.mqtt.client as mqtt

from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices
from core import log, jsontools
from core.setting import Setting
from shared.model import *


class MqttClient(object):
    def __init__(self, context, username=None, password=None, host=None, port=None):
        self._client=None
        self._context=context
        self._username=Setting.get_value(self._context, "mqtt.username","username")
        self._password=Setting.get_value(self._context, "mqtt.password","password")
        self._host=Setting.get_value(self._context, "mqtt.host","mqtt.host.de")
        self._port=int(Setting.get_value(self._context, "mqtt.port",1883))
        self._create_client()

    def __enter__(self):
        return self._client

    def __exit__(self, *args):
        self._client.disconnect()

    def _create_client(self):
        self._client=mqtt.Client()
        self._client.username_pw_set(username=self._username, password=self._password)
        self._client.connect(self._host, self._port)

        