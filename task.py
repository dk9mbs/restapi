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

    def __del__(self):
        print("bye bye to restapi context")

def execute_plugin(publisher, params):
    context=AppInfo.create_context(session.session_id)
    plugin=Plugin(context, publisher, 'execute')
    plugin.execute('after', {'input': params, 'output': {}})
    AppInfo.save_context(context)


@postfork
def post_fork():
    global session

    create_logger(__name__).info("logging in as system")
    session=Session()
    create_logger(__name__).info(f"logged in as system with sessionid: {session.session_id}")


@cron(40,2,-1,-1,-1)
def clear_disabled_sessions(self,num):
    create_logger(__name__).info("Daily timer job (cron)")
    execute_plugin('$cron_daily', {})

@timer(60, target='spooler')
def every_minute(signum):
    create_logger(__name__).info("60 seconds elapsed in the spooler")
    execute_plugin('$timer_every_minute', {})

@timer(3600, target='spooler')
def every_hour(signum):
    create_logger(__name__).info("3600 seconds elapsed in the spooler")
    execute_plugin('$timer_every_hour', {})


@spool
def async_action(arguments):
    context=AppInfo.create_context(session.session_id)
    create_logger(__name__).info("spool")
    AppInfo.save_context(context)




