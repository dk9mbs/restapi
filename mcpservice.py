"""
MCP-Server für das dk9mbs restapi-Ökosystem.

Core:     generische CRUD-Tools über den FetchXML-Endpunkt /v1.0/data
Plugins:  fachliche Tools kommen aus dem bestehenden restapi-Pluginsystem.
          Jede Zeile in api_mcp_tool wird zu einem MCP-Tool, das die Action
          /v1.0/action/<action> aufruft. Dahinter steckt ein ganz normales Plugin
          (api_event_handler: publisher=<action>, event='execute', type='before').

Installation:   pip install "mcp>=2" httpx pydantic jsonschema
Start lokal:    python mcpservice.py                                   (stdio)
Start remote:   MCP_TRANSPORT=streamable-http python mcpservice.py     (HTTP, hinter Apache + TLS)

Auth: API-Key eines eigenen MCP-Benutzers (Header 'apikey'). Welche Tabellen
lesbar/schreibbar sind, regelt die restapi selbst über api_group_permission.
"""
import json
import logging
import os
import sys
import xml.etree.ElementTree as ET
from typing import Any

import httpx
import jsonschema
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.mcpserver.tools import Tool
from pydantic import BaseModel, Field

# --------------------------------------------------------------------------- Konfiguration
API_BASE = os.getenv("DK9MBS_API_BASE", "https://dk9mbs.de/api").rstrip("/")
API_KEY = os.getenv("DK9MBS_API_KEY", "")                 # API-Key des MCP-Benutzers
READ_ONLY = os.getenv("DK9MBS_READ_ONLY", "1") == "1"     # Schreib-Tools standardmäßig gesperrt
# Optionale zusätzliche Einschränkung; leer = alles, was der MCP-Benutzer laut api_group_permission darf
ALLOWED_TABLES = {t.strip() for t in os.getenv("DK9MBS_TABLES", "").split(",") if t.strip()}
# Operatoren laut core/fetchxmlparser.py
OPERATORS = {
    "eq", "neq", "geq", "leq", "=", "<>", ">=", "<=",
    "null", "notnull", "like", "startsWith", "endsWith", "contains",
    "lastXminutes", "lastXhours", "lastXdays", "lastXmonth", "lastXyears",
    "olderThenXMinutes", "olderThenXHours",
}

log = logging.getLogger("dk9mbs-mcp")   # niemals print(): stdout gehört bei stdio dem MCP-Protokoll
mcp = MCPServer(
    "dk9mbs-restapi",
    instructions=(
        "Zugriff auf die dk9mbs restapi (metadatengetriebene Datenbank, z. B. IoT-Geräte und Sensoren). "
        "Vorgehen: 1) list_tables aufrufen, um die verfügbaren Tabellen mit Klartext-Namen zu sehen. "
        "2) describe_table für die passende Tabelle aufrufen, um Feldnamen, Typen und Verweise zu kennen. "
        "3) Erst dann query_records/get_record mit exakt diesen Feldnamen verwenden. "
        "Felder mit 'references' verweisen auf eine andere Tabelle; deren Klartext steht im Ergebnis als "
        "__<feld>@name. Keine Tabellen- oder Feldnamen raten."
    ),
)


# --------------------------------------------------------------------------- Modelle
class Condition(BaseModel):
    field: str = Field(description="Spaltenname, z. B. 'last_scan_on'")
    value: str = Field(default="", description="Vergleichswert als Text (bei null/notnull leer)")
    operator: str = Field(default="eq", description=f"Einer von: {', '.join(sorted(OPERATORS))}")


# --------------------------------------------------------------------------- Hilfsfunktionen
def _check_table(table: str) -> None:
    if ALLOWED_TABLES and table not in ALLOWED_TABLES:
        raise ToolError(f"Tabelle '{table}' ist für MCP nicht freigegeben. Erlaubt: {sorted(ALLOWED_TABLES)}")


def _check_write() -> None:
    if READ_ONLY:
        raise ToolError("Server läuft im Read-only-Modus (DK9MBS_READ_ONLY=1).")


def _add_filter(parent: ET.Element, conditions: list[Condition] | None, filter_type: str = "and") -> None:
    if not conditions:
        return
    if filter_type not in ("and", "or"):
        raise ToolError("filter_type muss 'and' oder 'or' sein.")
    flt = ET.SubElement(parent, "filter", type=filter_type)
    for c in conditions:
        if c.operator not in OPERATORS:
            raise ToolError(f"Operator '{c.operator}' nicht erlaubt.")
        ET.SubElement(flt, "condition", field=c.field, value=c.value, operator=c.operator)


def _to_xml(root: ET.Element) -> str:
    # ElementTree escaped alle Attributwerte (&, <, ", ...)
    return ET.tostring(root, encoding="unicode")


async def _request(path: str, *, xml: str | None = None, payload: Any = None) -> Any:
    headers = {"apikey": API_KEY} if API_KEY else {}
    async with httpx.AsyncClient(timeout=30) as client:
        if xml is not None:
            headers["Content-Type"] = "application/xml"
            resp = await client.post(f"{API_BASE}{path}", content=xml.encode("utf-8"), headers=headers)
        else:
            resp = await client.post(f"{API_BASE}{path}", json=payload, headers=headers)
    if resp.status_code >= 400:
        # Fehlertext der restapi an das Modell durchreichen (z. B. fehlende Berechtigung)
        raise ToolError(f"restapi {resp.status_code}: {resp.text[:500]}")
    try:
        return resp.json()
    except ValueError:
        return {"raw": resp.text}


async def _post(xml: str) -> Any:
    return await _request("/v1.0/data", xml=xml)


def _select_xml(table: str, fields: list[str] | None, conditions: list[Condition] | None,
                filter_type: str = "and") -> str:
    root = ET.Element("restapi", type="select")
    ET.SubElement(root, "table", name=table, alias="a")
    if fields:  # ohne <select> liefert die API alle Felder
        sel = ET.SubElement(root, "select")
        for f in fields:
            ET.SubElement(sel, "field", name=f, table_alias="a")
    _add_filter(root, conditions, filter_type)
    return _to_xml(root)


# --------------------------------------------------------------------------- Generische Tools
@mcp.tool()
async def list_tables() -> Any:
    """Listet alle Tabellen, die gelesen werden dürfen: technischer Name ('table'), Klartext ('label'),
    ID- und Beschreibungsfeld sowie ob Anlegen/Ändern/Löschen erlaubt ist.
    Immer zuerst aufrufen, um die passende Tabelle zu finden."""
    result = await _request("/v1.0/action/api_mcp_schema", payload={})
    tables = result.get("tables", []) if isinstance(result, dict) else []
    if ALLOWED_TABLES:
        tables = [t for t in tables if t.get("table") in ALLOWED_TABLES]
    return {"tables": tables}


@mcp.tool()
async def describe_table(table: str) -> Any:
    """Beschreibt die Felder einer Tabelle: name, label, type, is_primary_key, allow_null, is_read_only
    und 'references' (Tabelle, auf die ein *_id-Feld verweist).
    Vor query_records aufrufen, damit die Feldnamen stimmen."""
    _check_table(table)
    return await _request("/v1.0/action/api_mcp_schema", payload={"table": table})


@mcp.tool()
async def query_records(table: str, fields: list[str] | None = None,
                        conditions: list[Condition] | None = None, filter_type: str = "and") -> Any:
    """Liest Datensätze per FetchXML-Select.
    fields leer = alle Felder. Zu jedem Feld liefert die API zusätzlich __<feld>@formatted_value,
    bei *_id-Feldern außerdem __<feld>@name (Name des referenzierten Datensatzes, spart einen Join)."""
    _check_table(table)
    return await _post(_select_xml(table, fields, conditions, filter_type))


@mcp.tool()
async def get_record(table: str, record_id: str) -> Any:
    """Liest genau einen Datensatz anhand seiner id."""
    _check_table(table)
    return await _post(_select_xml(table, None, [Condition(field="id", value=record_id)]))


@mcp.tool()
async def insert_record(table: str, values: dict[str, str]) -> Any:
    """Legt einen Datensatz an. sys_row_id wird automatisch vergeben und darf nicht gesetzt werden.
    Der Platzhalter '{now}' als Wert setzt den aktuellen Zeitstempel."""
    _check_write()
    _check_table(table)
    root = ET.Element("restapi", type="insert")
    ET.SubElement(root, "table", name=table)
    flds = ET.SubElement(root, "fields")
    for k, v in values.items():
        if k != "sys_row_id":
            ET.SubElement(flds, "field", name=k, value=str(v))
    return await _post(_to_xml(root))


@mcp.tool()
async def update_record(table: str, record_id: str, values: dict[str, str]) -> Any:
    """Ändert Felder eines Datensatzes anhand seiner id."""
    _check_write()
    _check_table(table)
    root = ET.Element("restapi", type="update")
    ET.SubElement(root, "table", name=table)
    _add_filter(root, [Condition(field="id", value=record_id)])
    flds = ET.SubElement(root, "fields")
    for k, v in values.items():
        if k not in ("id", "sys_row_id"):
            ET.SubElement(flds, "field", name=k, value=str(v))
    return await _post(_to_xml(root))


# --------------------------------------------------------------------------- Plugin-Tools (Actions)
class ActionTool(Tool):
    """MCP-Tool mit frei definiertem JSON-Schema aus api_mcp_tool.input_schema.
    Validiert die Argumente selbst und reicht sie 1:1 an die Action weiter."""

    async def run(self, arguments: dict[str, Any], context: Any, convert_result: bool = False) -> Any:
        try:
            jsonschema.validate(arguments, self.parameters)
        except jsonschema.ValidationError as err:
            raise ToolError(f"Ungültige Argumente für {self.name}: {err.message}") from err
        result = await self.fn(arguments)
        return self.fn_metadata.convert_result(result) if convert_result else result


def _register_action_tool(row: dict[str, Any]) -> None:
    name = row["name"]
    action = row["action"]
    is_read_only = str(row.get("is_read_only", "0")) == "-1"
    if READ_ONLY and not is_read_only:
        log.info("Tool '%s' übersprungen (schreibend, Server ist read-only)", name)
        return
    try:
        schema = json.loads(row.get("input_schema") or "{}") or {"type": "object", "properties": {}}
    except ValueError:
        log.error("Tool '%s': input_schema ist kein gültiges JSON", name)
        return

    async def call_action(arguments: dict[str, Any]) -> Any:
        return await _request(f"/v1.0/action/{action}", payload=arguments)

    base = Tool.from_function(call_action, name=name, description=row.get("description") or name)
    tool = ActionTool(**{k: getattr(base, k) for k in Tool.model_fields})
    tool.parameters = schema
    # MCPServer.add_tool() baut das Schema aus der Funktionssignatur; für ein freies Schema
    # wird das fertige Tool direkt eingetragen.
    mcp._tool_manager._tools[name] = tool
    log.info("Tool registriert: %s -> /v1.0/action/%s", name, action)


async def load_action_tools() -> None:
    """Liest alle aktiven Einträge aus api_mcp_tool und registriert sie als MCP-Tools."""
    xml = _select_xml("api_mcp_tool", ["name", "description", "action", "input_schema", "is_read_only"],
                      [Condition(field="is_enabled", value="-1")])
    try:
        rows = await _post(xml)
    except Exception:
        log.exception("api_mcp_tool konnte nicht gelesen werden – nur generische Tools verfügbar")
        return
    for row in rows if isinstance(rows, list) else []:
        try:
            _register_action_tool(row)
        except Exception:
            log.exception("Tool '%s' konnte nicht registriert werden", row.get("name"))


# --------------------------------------------------------------------------- Start
if __name__ == "__main__":
    import anyio

    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    anyio.run(load_action_tools)
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "stdio":
        mcp.run()
    else:
        from mcp.server.transport_security import TransportSecuritySettings

        # Hinter einem Reverse Proxy (Apache) den öffentlichen Hostnamen erlauben,
        # z. B. MCP_PUBLIC_HOST=dk9mbs.de. Schutz gegen DNS-Rebinding bleibt aktiv.
        public_hosts = [h.strip() for h in os.getenv("MCP_PUBLIC_HOST", "").split(",") if h.strip()]
        security = TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=["127.0.0.1:*", "localhost:*", "[::1]:*"] + public_hosts,
            allowed_origins=["http://127.0.0.1:*", "http://localhost:*"] + [f"https://{h}" for h in public_hosts],
        )
        mcp.run(transport, host=os.getenv("MCP_HOST", "127.0.0.1"), port=int(os.getenv("MCP_PORT", "8765")),
                streamable_http_path=os.getenv("MCP_PATH", "/mcp"), transport_security=security)
