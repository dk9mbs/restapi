import importlib
import threading
import uuid
import time
import json

from core import log
from core.appinfo import AppInfo

logger=log.create_logger(__name__)

class SyncWrapper(object):
    def __init__(self,fn, context, plugin_context, params):
        super().__init__()
        self._fn=fn
        self._context=context
        self._plugin_context=plugin_context
        self._params=params

    def setDaemon(self, value):
        pass

    def start(self):
        connection=self._context.get_connection()
        cursor=connection.cursor()
        status_id=10

        try:
            self._fn(self._context,self._plugin_context, self._params)
        except Exception as err:
            logger.exception(f"Exception: {err}")
            self._plugin_context['response']['error_text']=str(err)
            status_id=20

        ProcessTools.set_process_status(self._context,self._plugin_context,status_id)


class AsyncWrapper(threading.Thread):
    def __init__(self,fn, context, plugin_context, params):
        super().__init__()
        self._fn=fn
        self._origin__context=context
        self._plugin_context=plugin_context
        self._params=params

        credentials=AppInfo.system_credentials()
        session_id=AppInfo.login(credentials['username'],credentials['password'])
        self._context=AppInfo.create_context(session_id)

    def run(self):
        connection=self._context.get_connection()
        cursor=connection.cursor()
        status_id=10

        try:
            self._fn(self._context,self._plugin_context, self._params)
        except Exception as err:
            logger.exception(f"Exception: {err}")
            self._plugin_context['response']['error_text']=str(err)
            status_id=20

        ProcessTools.set_process_status(self._context,self._plugin_context,status_id)

        AppInfo.save_context(self._context, True)
        AppInfo.logoff(self._context)


class Plugin:
    def __init__(self,context, publisher, trigger):
        self._context=context
        self._publisher=publisher
        self._trigger=trigger
        self._plugins=[]
        self.read()

    def read(self):
        sql=f"""
        select p.plugin_module_name,p.type,p.run_async,p.id,p.run_async,p.config
            from api_event_handler p
            WHERE
            p.publisher=%s AND p.event=%s
            ORDER BY sorting,id
        """

        connection=self._context.get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,[self._publisher, self._trigger])
        plugins=cursor.fetchall()
        self._plugins=plugins

    def execute(self, type, params):
        for p in self._plugins:

            if p['type']==type:
                plugin_context=ProcessTools.create_context(publisher=self._publisher, trigger=self._trigger,
                                type=type, event_handler_id=p['id'], run_async=p['run_async'], plugin_config=p['config'])

                mod=importlib.import_module(p['plugin_module_name'])

                ProcessTools.create_process(self._context,plugin_context,params)

                if p['run_async']==0:
                    task=SyncWrapper(mod.execute, self._context, plugin_context, params)
                    task.setDaemon(False)
                    task.start()
                else:
                    task=AsyncWrapper(mod.execute, self._context, plugin_context, params)
                    task.setDaemon(False)
                    task.start()



class ProcessTools(object):
    @staticmethod
    def create_process(context, plugin_context, params):
        connection=context.get_connection()
        cursor=connection.cursor()
        sql=f"INSERT INTO api_process_log (id,request_msg,event_handler_id,run_async,config) VALUES (%s,%s,%s,%s,%s)"
        cursor.execute(sql,[plugin_context['process_id'],
                    str(params), plugin_context['event_handler_id'],
                    plugin_context['run_async'], str(plugin_context['config'])
                ])
        connection.commit()


    @staticmethod
    def set_process_status(context,plugin_context, status_id):
        connection=context.get_connection()
        cursor=connection.cursor()

        if str(plugin_context['response']['status_code'])!="0" and str(plugin_context['response']['status_code'])!="200":
            status_id=20

        sql=f"UPDATE api_process_log SET response_code=%s,response_msg=%s,status_id=%s,error_text=%s,response_on=NOW() WHERE id=%s"
        cursor.execute(sql,[plugin_context['response']['status_code'],plugin_context['response']['payload'],
                            status_id,plugin_context['response']['error_text'], plugin_context['process_id']])

        connection.commit()

    @staticmethod
    def create_context(publisher, trigger, type, event_handler_id, run_async, plugin_config, **kwargs):
        response={}
        response['status_code']="0"
        response['payload']=None
        response['error_text']=None
        response['cancel']=False

        config={}
        if not plugin_config==None and not plugin_config=="":
            config=json.loads(plugin_config)

        return {"publisher":publisher, "trigger":trigger, "type":type,
                "process_id":str(uuid.uuid4()),
                "cancel":False,
                "event_handler_id": event_handler_id,
                "run_async": run_async,
                "config": config,
                "response": response }





