from core import log

logger=log.create_logger(__name__)

#
# Beispiel-Plugin für ein MCP-Tool (siehe api_mcp_tool in install/db/basedata.sql).
# Aufruf über /v1.0/action/api_mcp_demo
#
# params['input']={}    -> keine Parameter
#
def config():
    return {"raise_exception": True}

def execute(context, plugin_context, params):
    params['output']['message']="Hello World!"
    params['output']['username']=context.get_username()
