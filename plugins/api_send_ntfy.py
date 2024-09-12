import requests

from config import CONFIG
from core.appinfo import AppInfo
from core.plugin import Plugin
from core import log
from core.setting import Setting
from services.table_info import TableInfo
from services.activity import Activity

logger=log.create_logger(__name__)

def _validate(params):
    if 'data' not in params:
        return False
    if 'subject' not in params['data']:
        return False
    if 'msg_text' not in params['data']:
        return False
    if 'type_id' not in params['data']:
        return False

    return True

def config():
      return {"raise_exception": False}

def execute(context, plugin_context, params):
    if not _validate(params):
        logger.warning(f"Missings params {params}")
        return 

    subject=params['data']['subject']['value']
    msg_text=params['data']['msg_text']['value']
    type_id=int(params['data']['type_id']['value'])

    #only in case of alerts!
    if type_id!=4:
        return

    url=Setting.get_value(context,"ntfy.url","https://ntfy.sh")
    topic=Setting.get_value(context,"ntfy.topic","mytopic")
    username=Setting.get_value(context,"ntfy.username","username")
    password=Setting.get_value(context,"ntfy.password","password")

    #requests.post("https://ntfy.sh/restapi-test", data=f"{subject}".encode(encoding='utf-8'))
    requests.post(f"{url}/{topic}",
    data=f"{msg_text}",
    headers={
        "Title": f"{subject}",
        "Priority": "urgent",
        "Tags": "warning"
    })
