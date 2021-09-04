from core import log
import urllib


logger=log.create_logger(__name__)

class HTTPRequest:
    @staticmethod
    def redirect(request):
        next=""
        redirect_key="redirect"

        if not redirect_key in request.args:
            return None

        next = request.args.get(redirect_key)
        if next == "" or next == None:
            return None

        return urllib.parse.unquote(next)
