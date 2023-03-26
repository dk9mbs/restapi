import time
import json
import threading
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

class TaskQueueWorker():
    def __init__(self, session_id):
        self._context=None
        self._run=True
        self._session_id=session_id

    def __set_process_status(self, process_id, status_id):
        fetch=f"""
        <restapi type="update">
            <table name="api_process_log"/>
            <fields>
                <field name="status_id" value="{status_id}"/>
            </fields>
            <filter type="and">
                <condition field="id" value="{process_id}" operator="="/>
            </filter>
        </restapi>
        """
        fetchparser=FetchXmlParser(fetch, self._context)
        rs=DatabaseServices.exec(fetchparser, self._context,run_as_system=True, fetch_mode=0)

    def __is_process_waiting(self, process_id):
        return True
        fetch=f"""
        <restapi type="select">
            <table name="api_process_log" alias="p"/>
            <select>
                <field name="status_id" table_alias="p" />
            </select>
            <filter type="and">
                <condition field="id" value="{process_id}" operator="="/>
            </filter>
        </restapi>
        """
        fetchparser=FetchXmlParser(fetch, self._context)
        rs=DatabaseServices.exec(fetchparser, self._context,run_as_system=True, fetch_mode=0)

        if rs.get_eof():
            return False

        if rs.get_result()[0]['status_id']==0:
            return True
        else:
            return False

    def run_waiting_tasks(self):
        fetch=f"""
        <restapi type="select">
            <table name="api_process_log" alias="a"/>
            <select>
                <field name="id" table_alias="a"/>
                <field name="request_msg" table_alias="a"/>
                <field name="event" table_alias="e"/>
                <field name="type" table_alias="e"/>
                <field name="publisher" table_alias="e"/>
                <field name="event_handler_id" table_alias="a"/>
            </select>
            <joins>
                <join type="inner" table="api_event_handler" alias="e" condition="e.id=a.event_handler_id"/>
            </joins>
            <filter type="and">
                <condition field="status_id" value="0" alias="a" operator="="/>
                <condition field="run_async" value="-1" alias="a" operator="="/>
                <condition field="run_queue" value="-1" alias="e" operator="="/>
            </filter>
        </restapi>
        """
        fetchparser=FetchXmlParser(fetch, self._context)
        rs=DatabaseServices.exec(fetchparser, self._context,run_as_system=True, fetch_mode=0)
        for proc in rs.get_result():
            if self.__is_process_waiting(proc['id']):
                self.__set_process_status(proc['id'], 5)
                create_logger(__name__).info(f"executing plugin from process list: {proc['id']}")
                params=json.loads(proc['request_msg'])
                plugin=Plugin(self._context, proc['publisher'], proc['event'], process_id=proc['id'])
                plugin.execute(proc['type'], params)

    def execute(self):
        self._context=AppInfo.create_context(self._session_id, auto_commit=False)
        self.run_waiting_tasks()
        AppInfo.save_context(self._context, close_context=True)


class TimerWorker():
    def __init__(self, session_id):
        self._context=None
        self._run=True
        self._session_id=session_id

    def kill(self):
        self._run=False

    def _execute_plugin(self,context, publisher, params):
        create_logger(__name__).info(publisher)
        plugin=Plugin(context, publisher, 'execute')
        plugin.execute('after', {'input': params, 'output': {}})

    def _every_minute(self):
        context=AppInfo.create_context(self._session_id)
        interval=int(context.get_session_values()['timer_interval'])+1
        context.get_session_values()['timer_interval']=interval
        unit=context.get_session_values()['timer_unit']
        create_logger(__name__).info(f"Interval: {interval}")
        AppInfo.save_context(context, close_context=False)

        #every minute
        self._execute_plugin(context, "$timer_every_minute", {})

        # every ten minutes
        if interval % 10 == 0:
            self._execute_plugin(context, "$timer_every_ten_minutes", {})

        # every hour
        if interval % 60 == 0:
            self._execute_plugin(context, "$timer_every_hour", {})

        # every day
        if datetime.now().minute==1 and datetime.now().hour==0:
            self._execute_plugin(context, "$timer_every_day", {})

        AppInfo.save_context(context)

    def execute(self):
        self._every_minute()


class Wait(threading.Thread):
    def __init__(self, timeout, session_id, callback):
        super().__init__()
        self._callback=callback
        self._timeout=timeout
        self._run=True
        self._session_id=session_id

    def kill(self):
        self._run=False

    def run(self):
        last=datetime.now()
        while self._run:
            current=datetime.now()
            delta = current - last
            if delta.total_seconds()>=self._timeout:
                last = datetime.now()
                self._callback(self._session_id)
            time.sleep(0.1)


class MqttWorker():
    def __init__(self, session_id):
        self._context=None
        self._run=True
        self._session_id=session_id
        self._client=None

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
            client.subscribe("owntracks/+/+")
            client.subscribe("owntracks/+/+/waypoints")

        def on_message(client, userdata, msg):
            context=AppInfo.create_context(self._session_id)

            params="{\"data\":"+msg.payload.decode('utf-8')+", \"topic\":\""+msg.topic+"\"}"

            self._execute_plugin(context, msg.topic.split("/")[0],params )
            self._execute_plugin(context, msg.topic, params )

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

def execute_timer(session_id):
    t=TimerWorker(session_id)
    t.execute()

def execute_queue(session_id):
    t=TaskQueueWorker(session_id)
    t.execute()

def main():
    session={}
    session['timer']=Session(name="timer")
    session['queue']=Session(name="queue", init_timer=False)
    session['mqtt']=Session(name="mqtt", init_timer=False)

    create_logger(__name__).info(f"timer logged in as system with sessionid: {session['timer'].session_id}")
    create_logger(__name__).info(f"queue logged in as system with sessionid: {session['queue'].session_id}")
    create_logger(__name__).info(f"queue logged in as system with sessionid: {session['mqtt'].session_id}")

    tasks=[]
    w_timer=Wait(60, session['timer'].session_id, execute_timer)
    w_timer.start()

    w_queue=Wait(30, session['queue'].session_id, execute_queue)
    w_queue.start()

    t=MqttWorker(session['mqtt'].session_id)
    t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt as err:
        create_logger(__name__).info("Waiting for shutdown threads...")

    t.kill()

    w_timer.kill()
    w_queue.kill()

    w_timer.join()
    w_queue.join()

main()
