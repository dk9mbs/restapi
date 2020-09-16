import decimal
from datetime import date, datetime, time, timedelta

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    if isinstance(obj, (timedelta)):
        return str(obj)
    if isinstance(obj, (decimal.Decimal)):
        return str(obj)
    raise TypeError ("Type %s not serializable" % type(obj))

