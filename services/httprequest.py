from core import log
import urllib


logger=log.create_logger(__name__)

class HTTPRequest:
    @staticmethod
    def redirect(request, default=None):
        next=""
        redirect_key="redirect"

        if not redirect_key in request.args:
            return default

        next = request.args.get(redirect_key)
        if next == "" or next == None:
            return default

        return urllib.parse.unquote(next)
