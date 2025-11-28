import datetime

from flask import make_response
from core import log
from services.orm import *
from shared.model import *
from core.context import Context

logger=log.create_logger(__name__)

class HTTPResponse:
    def __init__(self, context: Context, content):
        self._content=content
        self._headers={}
        self._context=context

        if self._context != None:
            headers=api_http_header.objects(self._context).select().where(api_http_header.enabled==1).to_list()
            for header in headers:
                self._headers[header.name.value] = header.value.value

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
