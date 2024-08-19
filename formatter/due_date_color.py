from datetime import datetime

def output(context, value, rec={}):
    if value==None:
        return "blue"

    delta=None

    date1=datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')
    date2=datetime.now()

    delta=(date1-date2).days

    if delta>0:
        return "lightgreen"
    elif delta==0:
        return "orange"
    else:
        return "red"

def input(context, value):
    return value