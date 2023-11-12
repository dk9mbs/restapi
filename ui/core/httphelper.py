
def build_query_string(context, append_args={}, remove_params=[], **kwargs):
    query=""
    args=context.get_args()
    args_builded={}

    for arg in args:
        value=args[arg]

        if arg in append_args:
            value=append_args[arg]

        args_builded[arg]=value

    for arg in append_args:
        if not arg in args_builded:
            args_builded[arg]=append_args[arg]

    for arg in args_builded:
        import urllib.parse
        value=urllib.parse.quote(str(args_builded[arg]))
        query=f"{query}&{arg}={value}"

    if query.startswith('&'):
        query=query[1:]

    query=f"?{query}"
    return query


