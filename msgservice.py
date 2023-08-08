import time
import json
import threading
import re
from datetime import datetime

from core.appinfo import AppInfo
from core.plugin import Plugin
from core.log import create_logger
from config import CONFIG
from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices
from core.plugin import ProcessTools
from core.setting import Setting

class Session:
    def __init__(self, name="default", init_timer=True):
        self._init_timer=init_timer
        self._name=name

        AppInfo.init(__name__, CONFIG['default'])
        user=AppInfo.system_credentials()
        self.session_id=AppInfo.login(user['username'],user['password'])
        if self.session_id==None:
            create_logger(__name__).info("username / password wrong or user is disaled")

        context=AppInfo.create_context(self.session_id)
        if init_timer==True:
            context.get_session_values()['timer_interval']=0
            context.get_session_values()['timer_unit']='m'

        AppInfo.save_context(context)


    def __del__(self):
        print(f"bye bye to restapi context: {self._name}")


class MqttWorker():
    def __init__(self, session_id):
        self._context=None
        self._run=True
        self._session_id=session_id
        self._client=None

        self._topics=[]
        self._topics.append({"topic": "owntracks/+/+","regex":"", "prefix":""})
        self._topics.append({"topic": "owntracks/+/+/waypoints","regex":"", "prefix":""})
        self._topics.append({"topic": "+/rpc","regex":"^shelly.*/rpc$", "prefix":"iot_shelly/"})

    def kill(self):
        self._run=False
        self._client.loop_stop()

    def _execute_plugin(self,context, publisher, params):
        plugin=Plugin(context, publisher, 'mqtt_message')
        plugin.execute('after', params)

    def start(self):
        import paho.mqtt.client as mqtt

        def on_connect(client, userdata, flags, rc):
            create_logger(__name__).info(f"MQTT Connect with result code:{str(rc)}")

            for t in self._topics:
                client.subscribe(t['topic'])
                create_logger(__name__).info(f"Subscribing topic: {t['topic']}")

            create_logger(__name__).info("connected!")

        def on_message(client, userdata, msg):
            context=AppInfo.create_context(self._session_id)

            params="{\"data\":"+msg.payload.decode('utf-8')+", \"topic\":\""+msg.topic+"\"}"
            topic=msg.topic

            for t in self._topics:
                if t['regex']!="" and t['regex']!=None:
                    if re.search(t['regex'], topic):
                        create_logger(__name__).info(f"Match: {topic}")
                        if t['prefix']!="":
                            topic=f"{t['prefix']}{topic}"

            create_logger(__name__).info(f"{topic}")
            create_logger(__name__).info(f"{params}")

            self._execute_plugin(context, topic.split("/")[0],params )
            self._execute_plugin(context, topic, params )

            AppInfo.save_context(context)

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        context=AppInfo.create_context(self._session_id)
        username=Setting.get_value(context, "mqtt.username","username")
        password=Setting.get_value(context, "mqtt.password","password")
        host=Setting.get_value(context, "mqtt.host","mqtt.host.de")
        port=Setting.get_value(context, "mqtt.port","1883")
        AppInfo.save_context(context)

        client.username_pw_set(username, password=password)
        client.connect(host, 1883, 60)
        self._client=client
        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        #client.loop_forever()
        client.loop_start()

def main():
    session={}
    session['mqtt']=Session(name="mqtt", init_timer=False)

    create_logger(__name__).info(f"msgservice logged in as system with sessionid: {session['mqtt'].session_id}")

    t=MqttWorker(session['mqtt'].session_id)
    t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt as err:
        create_logger(__name__).info("Waiting for shutdown threads...")

    t.kill()

main()
