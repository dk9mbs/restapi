import importlib
import threading
import uuid
import time
from core import log
from core.appinfo import AppInfo

logger=log.create_logger(__name__)

class Plugin:
    class AsyncWrapper(threading.Thread):
        def __init__(self,fn, context, plugin_context, params):
            super().__init__()
            self._fn=fn
            self._context=context
            self._plugin_context=plugin_context
            self._params=params
            self._params['response']={}
            self._params['response']['status_code']="-999"
            self._params['response']['payload']="No payload from plugin"


        def run(self):
            connection=AppInfo.create_connection()
            cursor=connection.cursor()
            status_id=10
            error_text=None

            sql=f"INSERT INTO api_process_log (id,request_msg) VALUES (%s,%s)"
            cursor.execute(sql,[self._plugin_context['process_id'],str(self._params)])
            connection.commit()

            try:
                self._fn(self._context,self._plugin_context, self._params)
            except Exception as err:
                logger.exception(f"Exception: {err}")
                error_text=str(err)
                status_id=20

            response_status_code=self._params['response']['status_code']
            response_payload=self._params['response']['payload']

            sql=f"UPDATE api_process_log SET response_code=%s,response_msg=%s,status_id=%s,error_text=%s,response_on=NOW() WHERE id=%s"
            cursor.execute(sql,[response_status_code,response_payload, status_id,error_text, self._plugin_context['process_id']])

            connection.commit()
            connection.close()





    def __init__(self,context, publisher, trigger):
        self._context=context
        self._publisher=publisher
        self._trigger=trigger
        self._plugins=[]
        self.read()

    def read(self):
        sql=f"""
        select p.plugin_module_name,p.type,p.run_async from api_event_handler p
            WHERE
            p.publisher=%s AND p.event=%s
            ORDER BY sorting
        """

        connection=self._context.get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,[self._publisher, self._trigger])
        plugins=cursor.fetchall()
        self._plugins=plugins

    def execute(self, type, params):
        for p in self._plugins:
            if p['type']==type:
                plugin_context=Plugin.create_context(publisher=self._publisher, trigger=self._trigger, type=type)
                mod=importlib.import_module(p['plugin_module_name'])

                if p['run_async']==0:
                    mod.execute(self._context,plugin_context, params)
                else:
                    task=self.AsyncWrapper(mod.execute, self._context, plugin_context, params)
                    task.setDaemon(False)
                    task.start()

    @staticmethod
    def create_context(publisher, trigger, type, **kwargs):
        return {"publisher":publisher, "trigger":trigger, "type":type,"process_id":str(uuid.uuid4()), "cancel":False }
