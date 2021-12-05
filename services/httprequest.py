from core import log
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
    def __replace_default(default, var_id, id):
        if default==None:
            return None
        else:
            return default.replace(var_id, id)
