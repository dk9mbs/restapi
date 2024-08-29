from config import CONFIG
from core.appinfo import AppInfo
from core.plugin import Plugin
from core import log
from services.table_info import TableInfo
from services.activity import Activity

logger=log.create_logger(__name__)

def _validate(params):
    if 'input' not in params:
        return False
    if 'subject' not in params['input']:
        return False
    if 'msg_text' not in params['input']:
        return False
    if 'tag' not in params['input']:
        return False
    if 'status_id' not in params['input']:
        return False

    return True

def config():
      return {"raise_exception": True}

def execute(context, plugin_context, params):
    if not _validate(params):
        logger.warning(f"Missings params {params}")
        raise Exception(f"Missings params {params}")
        
    activity=Activity(context)

    subject=params['input']['subject']
    msg_text=params['input']['msg_text']
    tag=params['input']['tag']
    status_id=params['input']['status_id']

    id=activity.create_alert_if_not_exists(subject,msg_text,tag,status_id)    

    params['output']['id']=id