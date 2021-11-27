def isnumeric(value):
    try:
        float(value)
        return True
    except:
        return False
