import importlib

import core.log

class Plugin:

    def __init__(self,context, publisher, trigger):
        self._context=context
        self._publisher=publisher
        self._trigger=trigger
        self._plugins=[]
        self.read()

    def read(self):
        sql=f"""
        select p.plugin_module_name,p.type from api_event_handler p 
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
                mod.execute(self._context,plugin_context, params)
                #cancel=bool(plugin_context['cancel'])

    @staticmethod
    def create_context(publisher, trigger, type, **kwargs):
        return {"publisher":publisher, "trigger":trigger, "type":type,"cancel":False }
