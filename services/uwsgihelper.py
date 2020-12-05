
def is_uwsgi_available():
    try:
        import uwsgi
        return True
    except:
        return False

def get_spool_fn():
    import task
    return task.async_action
