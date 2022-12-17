import time
from datetime import datetime

from core.appinfo import AppInfo
from core.plugin import Plugin
from core.log import create_logger
from config import CONFIG

class Session:
    def __init__(self):
        AppInfo.init(__name__, CONFIG['default'])
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





def every_minute():
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

    # every day
    if datetime.now().minute==1 and datetime.now().hour==0:
        execute_plugin(context, "$timer_every_day", {})


    AppInfo.save_context(context)



def main():
    global session

    create_logger(__name__).info("logging in as system")
    session=Session()
    create_logger(__name__).info(f"logged in as system with sessionid: {session.session_id}")

    while True:
        try:
            create_logger(__name__).info(f"starting interval (1 minute) ...")
            every_minute()
            create_logger(__name__).info(f"end of interval")
            time.sleep(60)
        except Exception as err:
            create_logger(__name__).exception(err)

main()
