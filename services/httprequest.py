from core import log
from core.context import Context
import urllib


logger=log.create_logger(__name__)

class HTTPRequest:
    @staticmethod
    def get_querystring_value(request, name, default=""):
        if name in request.args:
            return request.args[name]
        else:
            return default

    @staticmethod
    def redirect(request, default=None, **kwargs):
        next=""
        redirect_key="redirect" # in query

        id=""
        id_key="id" # in kwargs
        var_id='$$id$$'

        if id_key in kwargs:
            id=str(kwargs[id_key])

        if not redirect_key in request.args:
            return HTTPRequest.__replace_default(default, var_id, id)

        next = request.args.get(redirect_key)

        if next == "" or next == None:
            return HTTPRequest.__replace_default(default, var_id, id)

        return urllib.parse.unquote(next.replace(var_id, id))

    @staticmethod
    def process_command(request, context: Context) -> bool:
        if not 'api_cmd' in request.args:
            return False

        if not 'api_token' in request.args:
            return False

        token=request.args['api_token']
        command=request.args['api_cmd']

        # save the current http query args in the users session
        if command=='save':
            context.get_session_values()['saved_args'][token]=context.get_args()
            return False

        if command=='next_page':
            if 'page' in context.get_session_values()['saved_args'][token]:
                print(context.get_session_values()['saved_args'][token])
                context.get_session_values()['saved_args'][token]['page']=int(context.get_session_values()['saved_args'][token]['page'])+1

        if command=='previous_page':
            if 'page' in context.get_session_values()['saved_args'][token]:
                context.get_session_values()['saved_args'][token]['page']=int(context.get_session_values()['saved_args'][token]['page'])-1

        for key, value in context.get_session_values()['saved_args'][token].items():
            context.set_arg(key, value)

        return True

    @staticmethod
    def __replace_default(default, var_id, id):
        if default==None:
            return None
        else:
            return default.replace(var_id, id)
