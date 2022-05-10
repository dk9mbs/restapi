import decimal
import base64
from datetime import date, datetime, time, timedelta

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    if isinstance(obj, (timedelta)):
        return str(obj)
    if isinstance(obj, (decimal.Decimal)):
        return str(obj)
    if isinstance(obj, (bytes)):
        #message = "Python is fun"
        #message_bytes = message.encode('ascii')
        message_bytes = obj
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        return base64_message
    raise TypeError ("Type %s not serializable" % type(obj))


def merge(json1, json2):
    for key in json2:
        json1[key]=json2[key]

    return json1

