
def build_query_string(context, **kwargs):
    return f"?app_id={context.get_arg('app_id','1')}&system_created=yes"

