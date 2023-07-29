import uuid

from core import log
logger=log.create_logger(__name__)

def execute(context, plugin_context, params):
    params['data']['id']={}
    params['data']['id']['value']=str(uuid.uuid1())

