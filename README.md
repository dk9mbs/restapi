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
table change:
-data : in data
-response :outdata
-config : config from api_event_handler
