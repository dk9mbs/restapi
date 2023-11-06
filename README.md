api_token and api_cmd

http://localhost:5000/api/v1.0/data/api_table?view=$html_table&view_columns=id,name&page=0&page_size=10&api_token=test&api_cmd=save
http://localhost:5000/api/v1.0/data/api_table?api_token=test&api_cmd=next_page
http://localhost:5000/api/v1.0/data/api_table?api_token=test&api_cmd=previous_page
http://localhost:5000/api/v1.0/data/api_table?api_token=test&api_cmd=first_page




https://www.python.org/dev/peps/pep-0008/#function-and-variable-names
https://visualgit.readthedocs.io/en/latest/pages/naming_convention.html

Upload a file:
curl -F "file=@test.jpg;filename=test.jpg" http://localhost:5000/api/v1.0/file


a2enmodule proxy_http

params:

action:
-input
-output

event:
table change or create:
-data : in data

app on statrt: 
params: {}

timer:
params: {}

plugin_context:
-response :outdata
-config : config from api_event_handler

control_config:
- disabled:True
- mode: ace/mode/html (aceEdit)


fetchxmlparser.get_columns():
{"table": table, "database_field": name, "label": column_header, "alias": alias, "formatter": formatter}

