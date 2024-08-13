from datetime import datetime

def output(context, value):
    if value == None:
        return None
    
    tmp=datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')
    return tmp.strftime('%d.%m.%Y')

def input(context, value):
    return value