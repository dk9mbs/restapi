import datetime
import requests
import json

from core import log, jsontools
from core.xml_reader import XmlReader

logger=log.create_logger(__name__)

def execute(context, plugin_context, params):
    if 'data' in params:
        payload=params['data']

    file=params['data']['file_full_name']
    format=params['data']['format']

    f=open(file,'rb')
    xml=f.read()
    f.close()

    reader=XmlReader(context, format, xml)
    reader.read()
