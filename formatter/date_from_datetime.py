from datetime import datetime

def output(context, field_name, value, rec={}):
    if value == None:
        return None
    
    tmp=datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')
    return tmp.strftime('%d.%m.%Y')

def input(context, value):
    return value