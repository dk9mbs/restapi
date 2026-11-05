import secrets

from core import log
logger=log.create_logger(__name__)

def execute(context, plugin_context, params):
    # 32 Byte aus dem kryptografischen Zufallsgenerator (64 Hex-Zeichen)
    params['data']['id']={}
    params['data']['id']['value']=secrets.token_hex(32)
