import datetime

from flask import make_response
from core import log

logger=log.create_logger(__name__)

class HTTPResponse:
    def __init__(self, content):
        self._content=content
        self._headers={}

    def disable_client_cache(self):
        self._headers['Last-Modified'] = datetime.datetime.now()
        self._headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        self._headers['Pragma'] = 'no-cache'
        self._headers['Expires'] = '-1'

    def add_header(self, key, value):
        self._headers[key]=value

    def create_response(self):
        response=make_response(self._content)

        for key, value in self._headers.items():
            response.headers[key]=value

        return response
