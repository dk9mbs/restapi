from core.appinfo import AppInfo
from core.plugin import Plugin
from core.log import create_logger
from uwsgidecorators import *

class Session:
    def __init__(self):
        user=AppInfo.system_credentials()
        self.session_id=AppInfo.login(user['username'],user['password'])
        if self.session_id==None:
            create_logger(__name__).info("username / password wrong or user is disaled")

        context=AppInfo.create_context(self.session_id)
        context.get_session_values()['timer_interval']=0
        context.get_session_values()['timer_unit']='m'
        AppInfo.save_context(context)


    def __del__(self):
        print("bye bye to restapi context")

def execute_plugin(context, publisher, params):
    create_logger(__name__).info(publisher)
    plugin=Plugin(context, publisher, 'execute')
    plugin.execute('after', {'input': params, 'output': {}})


@postfork
def post_fork():
    global session

    create_logger(__name__).info("logging in as system")
    session=Session()
    create_logger(__name__).info(f"logged in as system with sessionid: {session.session_id}")



#@cron(40,2,-1,-1,-1)
#def clear_disabled_sessions(self,num):
#    create_logger(__name__).info("Daily timer job (cron)")
#    execute_plugin('$cron_daily', {})


@timer(60, target='spooler')
def every_minute(signum):
    context=AppInfo.create_context(session.session_id)

    interval=int(context.get_session_values()['timer_interval'])+1
    context.get_session_values()['timer_interval']=interval
    unit=context.get_session_values()['timer_unit']
    create_logger(__name__).info(f"Interval: {interval}")
    AppInfo.save_context(context, close_context=False)

    #every minute
    execute_plugin(context, "$timer_every_minute", {})

    # every ten minutes
    if interval % 10 == 0:
        execute_plugin(context, "$timer_every_ten_minutes", {})

    # every hour
    if interval % 60 == 0:
        execute_plugin(context, "$timer_every_hour", {})


    AppInfo.save_context(context)



@spool
def async_action(arguments):
    context=AppInfo.create_context(session.session_id)
    create_logger(__name__).info("spool")
    AppInfo.save_context(context)




