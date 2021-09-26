from core import log
import urllib


logger=log.create_logger(__name__)

class HTTPRequest:
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
            return default.replace(var_id, id)

        next = request.args.get(redirect_key)

        if next == "" or next == None:
            return default.replace(var_id, id)

        return urllib.parse.unquote(next.replace(var_id, id))

