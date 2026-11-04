# restapi

A metadata-driven REST API framework built on **Flask**, **flask-restx** and **MySQL/MariaDB** (PyMySQL).

Almost nothing about the data model is hardcoded: tables, fields, views, permissions, formatters and lookups are rows in the `api_table*`, `api_group_permission` and `api_table_view` tables and are read at request time. Application-specific behaviour (bank imports, IoT/MQTT devices, APRS, ham-radio ADIF logging, …) lives in **plugins**: ordinary Python modules registered in the `api_event_handler` table.

## Features

- Generic CRUD API for every table registered in the metadata
- Three query front ends: **FetchXML** (XML mini-DSL), **FetchSQL** (real SQL, validated with `sqlglot`) and a small Django-style **ORM**
- Table-level permissions per group (`api_group_permission`), checked on every statement
- Plugin/event system for table changes, app start, timers and custom actions (`/v1.0/action/<action>`)
- Several ways to log in: session cookie, username/password, API key and **JWT** (access and refresh token)
- Jinja-based admin UI and portal
- **MCP server** (`mcpservice.py`) so AI assistants such as Claude can browse and query the data model

## Requirements

- Debian (Bullseye or Bookworm), Python 3.11 with `venv`
- MySQL or MariaDB (the install scripts use MariaDB syntax such as `ADD COLUMN IF NOT EXISTS`)
- Optional: Apache 2 as a reverse proxy, uwsgi and systemd for production
- MCP server: Python ≥ 3.10, installed in its own venv

## Installation

```bash
git clone https://github.com/dk9mbs/restapi.git
cd restapi
cp config.skelet config.py      # then edit config.py (see below)
./install.sh <restapi_user> <restapi_password>
```

`install.sh`:
1. creates the virtual environment `venv/restapi` and installs the Python requirements (via `init.sh`)
2. creates the database and loads `install/db/install.sql` and `install/db/basedata.sql`
3. builds the metadata cache with `tools/metadata.py`, then runs `install/db/post_metacache.sql`
4. writes the systemd units `restapi.<instance>.service`, `restapi-timer.<instance>.service`, `restapi-msg.<instance>.service` and `restapi-mcp.<instance>.service`

### Configuration

`config.py` is not under version control. Start from `config.skelet`:

```python
CONFIG={
    "default": {
        "mysql": {"user":"username", "password":"password", "host":"localhost", "database":"databasename"},
        "instance": {"id":"give_me_a_id", "enable_swagger_doc":0},
        "server": {"port":5000, "host":"127.0.0.1"},
        "plugin": {"root":"/tmp"},
        "ui": {"wwwroot": "/tmp/wwwroot/"},
        "jwt": {"secret":"change_me_min_32_chars_e.g._openssl_rand_hex_32", "algorithm":"HS256",
            "access_lifetime_min":60, "refresh_lifetime_min":1440},
    }
}
```

The `jwt` section is required. Use a random secret with at least 32 bytes for HS256, e.g. from `openssl rand -hex 32`.

## Running

```bash
. ./init.sh          # activates venv/restapi and sets PYTHONPATH
python restapi.py    # development server, uses CONFIG['default']
```

In production the app runs under uwsgi/systemd. Apache examples are in `examples/apache2/`.

## API overview

All API endpoints are under `/api`, the admin UI under `/ui`, the portal under `/`.

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v1.0/core/login` | POST | Log in; returns `session_id`, `access_token`, `refresh_token` |
| `/api/v1.0/core/refresh` | POST | Exchange a refresh token for a new access token |
| `/api/v1.0/core/logoff` | POST | Log off |
| `/api/v1.0/data` | POST | Execute a FetchXML statement (body) |
| `/api/v1.0/data/<table>` | GET / POST | List or insert records |
| `/api/v1.0/data/<table>/<id>` | GET / PUT / DELETE | Read, update or delete a record |
| `/api/v1.0/data/view/<table>/<view>` | GET | Records rendered through a view |
| `/api/v1.0/file`, `/api/v1.0/file/<path>` | POST / PUT / GET | File upload and download (GET needs `<path>`) |
| `/api/v1.0/import/<format>` | POST | Text/file imports |
| `/api/v1.0/action/<action>` | POST | Run a plugin action; JSON body = `input`, response = `output` |

### Authentication

Resolved per request in this order:

1. `Authorization: Bearer <access_token>` (JWT)
2. session cookie
3. `restapi-username` / `restapi-password` headers
4. `username` / `password` headers or query parameters
5. `apikey` header or query parameter
6. anonymous guest login (auto logoff)

```bash
curl -X POST http://localhost:5000/api/v1.0/core/login \
     -H "username: root" -H "password: <password>"

curl http://localhost:5000/api/v1.0/data/api_table \
     -H "Authorization: Bearer <access_token>"
```

### FetchXML example

```xml
<restapi type="select">
    <table name="api_table" alias="a"/>
    <select>
        <field name="id" table_alias="a"/>
        <field name="name" table_alias="a"/>
    </select>
    <filter type="and">
        <condition field="alias" value="api_" operator="startsWith"/>
    </filter>
</restapi>
```

```bash
curl -X POST http://localhost:5000/api/v1.0/data \
     -H "Content-Type: application/xml" -H "apikey: <key>" \
     --data-binary @query.xml
```

## Architecture

```
api/ ui/      Flask-restx endpoints (one Resource class + get_endpoint() per module)
services/     service layer (DatabaseServices.exec, ORM, formatters, templates)
core/         core layer (AppInfo, Context, parsers, metadata, permissions, plugin runner)
plugins/      application logic, registered in api_event_handler
install/      SQL schema, base data, Python requirements
tools/        maintenance scripts (metadata cache, solutions)
```

Layering: **plugins → services → core**.

- `FetchXmlParser`, `FetchSqlParser` and `OrmParser` all produce `(sql, params)`. `DatabaseServices.exec()` checks the permissions and runs the statement.
- `core/meta.py` reads the table and field metadata from the database. `tools/metadata.py` precomputes the cache and generates `shared/model.py` for the ORM.

## Plugins

A plugin is a Python module in `plugins/` with an `execute()` function:

```python
def config():
    return {"raise_exception": True}

def execute(context, plugin_context, params):
    params['output']['message']="Hello World!"
```

Register it in `api_event_handler` (`plugin_module_name`, `publisher`, `event`, `type`). For an action, set `publisher=<action>`, `event='execute'`, `type='before'`; it is then available at `/api/v1.0/action/<action>`.

Plugins must not run SQL directly:
- **data access:** `DatabaseServices.exec(parser, context)` with a FetchXML, FetchSQL or ORM parser
- **system-level functions** (permissions, metadata): functions in `core/`

Plugin parameters by trigger:

| Trigger | `params` |
|---|---|
| action | `input`, `output` |
| table change / create | `data` |
| app start (`$app_start`) | `{}` |
| timer | `{}` |

`plugin_context` provides `response` (output data) and `config` (from `api_event_handler`).

## MCP server

`mcpservice.py` is a standalone [Model Context Protocol](https://modelcontextprotocol.io) server. It talks to the running restapi over HTTP using the API key of a dedicated MCP user, so table access follows that user's `api_group_permission` rows.

- **Generic tools:** `list_tables`, `describe_table`, `query_records`, `get_record`, `insert_record`, `update_record`. The write tools are disabled unless `DK9MBS_READ_ONLY=0`.
- **Custom tools:** every enabled row in `api_mcp_tool` becomes an MCP tool that calls `/v1.0/action/<action>`. To add one, write a plugin, register it as an action and insert an `api_mcp_tool` row with a JSON schema. See `api_mcp_demo` in `install/db/basedata.sql`.

`install.sh` creates `venv/mcp`, the configuration file `/etc/restapi/mcp.<instance>.env` (add the API key there) and the unit `restapi-mcp.<instance>.service`. Restart the service after changing `api_mcp_tool`.

For remote access, put it behind Apache with TLS and a bearer token:
- `examples/apache2/mcp.conf`: `Include` it in an existing `<VirtualHost *:443>` (endpoint `/mcp`)
- `examples/apache2/mcp-site.conf`: own host name, enable with `a2ensite` (endpoint `/`)

## Tests

The tests use `unittest` and need a **live database** configured in `config.py`. They log in as `root` / `password`.

```bash
. ./init.sh
python -m unittest discover -v -s test
python -m unittest test.test_fetchsqlparser -v
```

## Code style

The code base deliberately does not follow PEP 8 spacing: no spaces around `=` in assignments and keyword arguments (`x=1`, `foo(a=1)`). Please match the surrounding style.

## Developer notes

### `api_token` and `api_cmd` (server-side paging)

```
http://localhost:5000/api/v1.0/data/api_table?view=$html_table&view_columns=id,name&page=0&page_size=10&api_token=test&api_cmd=save
http://localhost:5000/api/v1.0/data/api_table?api_token=test&api_cmd=next_page
http://localhost:5000/api/v1.0/data/api_table?api_token=test&api_cmd=previous_page
http://localhost:5000/api/v1.0/data/api_table?api_token=test&api_cmd=first_page
```

### File upload

```bash
curl -F "file=@test.jpg;filename=test.jpg" http://localhost:5000/api/v1.0/file
```

### `control_config`

- `disabled: true`
- `mode: ace/mode/html` (ACE editor)

### `FetchXmlParser.get_columns()`

```python
{"table": table, "database_field": name, "label": column_header, "alias": alias, "formatter": formatter}
```

### MQTT topics

```
solutions:  restapi/extension/[solutionname]
            restapi/solution/[solutionname]
core:       restapi/core/[scope]
```

### Naming conventions (references)

- https://www.python.org/dev/peps/pep-0008/#function-and-variable-names
- https://visualgit.readthedocs.io/en/latest/pages/naming_convention.html
