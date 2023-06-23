import decimal
import base64
from datetime import date, datetime, time, timedelta
import xml.etree.ElementTree as ET

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    if isinstance(obj, (timedelta)):
        # time only format
        d=datetime(1970,1,1,0,0,0,0)+obj
        #return str(obj) # do not use: 06:13:12 will be returned as 6:13:45
        return str(d.time())
    if isinstance(obj, (decimal.Decimal)):
        return str(obj)
    if isinstance(obj, (bytes)):
        #message = "Python is fun"
        #message_bytes = message.encode('ascii')
        message_bytes = obj
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        return base64_message
    if isinstance(obj, ET.Element):
        return ET.tostring(obj, encoding='unicode')
    raise TypeError ("Type %s not serializable" % type(obj))


def merge(json1, json2):
    for key in json2:
        json1[key]=json2[key]

    return json1

