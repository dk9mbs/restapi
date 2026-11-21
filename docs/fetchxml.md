# Datenzugriff mit FetchXML

FetchXML ist die XML-basierte Abfragesprache der restapi. `core/fetchxmlparser.py` (`FetchXmlParser`) übersetzt sie in parametrisiertes SQL, `services/database.py` (`DatabaseServices.exec`) prüft die Rechte und führt es aus.

Alle Beispiele in diesem Dokument wurden gegen eine Dev-Instanz getestet (Tabelle `dummy`).

## Endpunkte

| Methode | URL | Zweck |
|---|---|---|
| `POST` | `/api/v1.0/data` | Beliebige FetchXML (`select`, `insert`, `update`, `delete`) im Body |
| `POST` | `/api/v1.0/data/search/<table>` | Suche: FetchXML im Body, der `<table>`-Knoten wird durch `<table>` aus der URL ersetzt |
| `GET` | `/api/v1.0/data/view/<table>/<view>` | Gespeicherte FetchXML aus `api_table_view` |

- **Body:** Die FetchXML kommt roh in den Body, mit `Content-Type: text/xml` oder `application/xml`. Formular-Content-Types sind nicht geeignet, Flask liest den Body dann als Formular.
- **Query-Parameter für `/api/v1.0/data`:**
  - `page` (Vorgabe 0) und `page_size` (Vorgabe 5000) für das Blättern
  - `query_lang`: `xml` (Vorgabe) oder `sql` für FetchSQL (`core/fetchsqlparser.py`)
- **Anmeldung:** wie bei allen Endpunkten, also JWT, Session-Cookie, `username`/`password`-Header oder `apikey`.

Beispiel mit `curl`:

```bash
curl -X POST "https://<host>/api/v1.0/data" \
  -H "apikey: <key>" -H "Content-Type: text/xml" \
  --data '<restapi type="select"><table name="dummy"/></restapi>'
```

## Aufbau

```xml
<restapi type="select" limit="10" offset="0">
    <table name="dummy" alias="d"/>
    <joins>...</joins>
    <select>...</select>
    <fields>...</fields>
    <filter type="AND">...</filter>
    <orderby>...</orderby>
    <comment text="..."/>
</restapi>
```

| Element / Attribut | Bedeutung |
|---|---|
| `type` | Pflicht: `select`, `insert`, `update` oder `delete`. `read` und `create` werden auch akzeptiert (siehe Hinweise) |
| `limit`, `offset` | Optional: begrenzen die Treffer (`LIMIT offset, limit`). Ohne diese Attribute gelten `page` und `page_size` |
| `<table name alias>` | Pflicht: die Haupttabelle. `name` ist der **Alias aus `api_table.alias`**, nicht zwingend der echte Tabellenname. `alias` ist der SQL-Alias, Vorgabe ist der Tabellenname |
| `<joins>` | Weitere Tabellen (nur bei `select` sinnvoll) |
| `<select>` | Spaltenauswahl. Fehlt das Element, werden alle Felder geliefert |
| `<fields>` | Werte für `insert` und `update` |
| `<filter>` | `WHERE`-Bedingung |
| `<orderby>` | Sortierung |
| `<comment text>` | Wird als `/* ... */` an das SQL angehängt, nützlich im Slow-Query-Log |

## Lesen (`select`)

### Alle Felder

```xml
<restapi type="select">
    <table name="dummy" alias="d"/>
    <filter type="AND">
        <condition field="name" operator="eq" value="fx-doc-test"/>
    </filter>
</restapi>
```

Ohne `<select>` liefert die restapi alle nicht-virtuellen Felder aus `api_table_field`. Zu jedem Feld gibt es zusätzlich `__<feld>@formatted_value`. Lookup-Felder (Verweise auf eine andere Tabelle) bekommen außerdem `__<feld>@name` (Klartext des verknüpften Datensatzes) und `__<feld>@url`:

```json
[
    {
        "id": 990001,
        "__id@formatted_value": 990001,
        "name": "fx-doc-test",
        "__name@formatted_value": "fx-doc-test",
        "Port": 4711,
        "__Port@formatted_value": 4711
    }
]
```

Plugins (`after select`) und Formatter können weitere Felder hinzufügen.

### Bestimmte Felder

```xml
<restapi type="select" limit="1">
    <table name="dummy" alias="d"/>
    <select>
        <field name="id"/>
        <field name="name" alias="bezeichnung"/>
    </select>
    <filter>
        <condition field="name" operator="startsWith" value="fx-doc"/>
    </filter>
    <orderby>
        <field name="id" sort="DESC"/>
    </orderby>
</restapi>
```

```json
[ { "id": 990002, "bezeichnung": "fx-doc-test" } ]
```

Attribute von `<select><field .../>`:

| Attribut | Bedeutung |
|---|---|
| `name` | Pflicht: Feldname. Muss in `api_table_field` existieren, sonst Fehler `Table: dummy on field: ...` |
| `alias` | Name der Spalte im Ergebnis |
| `table_alias` | Tabelle des Feldes (SQL-Alias aus `<table>` oder `<join>`), Vorgabe ist die Haupttabelle |
| `func` | SQL-Funktion um das Feld, z. B. `count`, `sum`, `min`, `max`, `avg`, `upper` |
| `format` | Bei `func="date_format"` Pflicht, z. B. `format="%d.%m.%Y"` |
| `string_before`, `string_after` | Bei `func="concat"`: Text vor bzw. nach dem Feld |
| `grouping` | Wenn vorhanden (beliebiger Wert), wird das Feld in `GROUP BY` aufgenommen |
| `header`, `formatter` | Spaltenüberschrift und Formatter für Views (`?view=...`) |

### Gruppieren und zählen

```xml
<restapi type="select">
    <table name="dummy" alias="d"/>
    <select>
        <field name="Port" grouping="y"/>
        <field name="id" func="count" alias="anzahl"/>
    </select>
    <filter>
        <condition field="name" value="fx-doc-test"/>
    </filter>
</restapi>
```

```json
[ { "Port": 4711, "anzahl": 1 }, { "Port": 4712, "anzahl": 1 } ]
```

### Joins

```xml
<restapi type="select">
    <table name="api_user" alias="u"/>
    <joins>
        <join table="api_user_group" alias="ug" type="inner" condition="ug.user_id=u.id"/>
    </joins>
    <select>
        <field name="username" table_alias="u"/>
        <field name="group_id" table_alias="ug"/>
    </select>
</restapi>
```

| Attribut | Bedeutung |
|---|---|
| `table` | Pflicht: Alias aus `api_table.alias` |
| `alias` | SQL-Alias |
| `type` | `inner` (Vorgabe), `left`, `right` |
| `condition` | Pflicht: die `ON`-Bedingung als SQL-Text |

Das Leserecht wird für jede verknüpfte Tabelle geprüft.

### Sortieren

```xml
<orderby>
    <field name="Port" sort="DESC"/>
    <field name="id" alias="d"/>
</orderby>
```

`sort` ist `ASC` (Vorgabe) oder `DESC`. `alias` ist der SQL-Alias der Tabelle, Vorgabe ist die Haupttabelle.

### Blättern

Mit Query-Parametern:

```
POST /api/v1.0/data?page=1&page_size=1
```

`page` beginnt bei 0. Alternativ setzt du `limit` und `offset` direkt am `<restapi>`-Knoten. Mische beides nicht: Ein `limit`-Attribut ersetzt nur `page_size`, der Offset wird dann trotzdem aus `page × page_size` berechnet. Mit `limit` deshalb auch `offset` angeben.

### Suche über `/data/search/<table>`

```bash
curl -X POST ".../api/v1.0/data/search/dummy" -H "Content-Type: text/xml" --data \
'<restapi type="select">
    <select><field name="id"/></select>
    <filter><condition field="name" operator="contains" value="doc-te"/></filter>
</restapi>'
```

Ein `<table>`-Knoten im Body wird entfernt und durch die Tabelle aus der URL ersetzt.

## Filter

```xml
<filter type="AND">
    <condition field="name" value="fx-doc-test"/>
    <filter type="OR">
        <condition field="id" value="990001"/>
        <condition field="id" value="990003"/>
    </filter>
</filter>
```

ergibt `(d.name=%s AND (d.id=%s OR d.id=%s))`.

- **`<filter type>`:** `AND` (Vorgabe) oder `OR`. Damit werden die Bedingungen dieses Filters verknüpft. Filter lassen sich verschachteln. Unterfilter werden mit dem `type` des umgebenden Filters verknüpft.
- **`<condition>`:**
  - `field`: Pflicht, der Spaltenname in der Datenbank
  - `alias`: SQL-Alias der Tabelle, Vorgabe ist die Haupttabelle
  - `operator`: Vorgabe `=`
  - `value`: der Vergleichswert. Er wird immer als SQL-Parameter übergeben, nicht in das SQL eingebaut.

| Operator | SQL |
|---|---|
| `eq` oder `=` | `feld = wert` |
| `neq` oder `<>` | `feld <> wert` |
| `geq` oder `>=` | `feld >= wert` |
| `leq` oder `<=` | `feld <= wert` |
| `like` | `feld LIKE wert` (Platzhalter `%` selbst setzen) |
| `startsWith` | `feld LIKE 'wert%'` |
| `endsWith` | `feld LIKE '%wert'` |
| `contains` | `feld LIKE '%wert%'` |
| `null` | `feld IS NULL` (ohne `value`) |
| `notnull` | `feld IS NOT NULL` (ohne `value`) |
| `lastXminutes` / `lastXhours` / `lastXdays` / `lastXmonth` / `lastXyears` | `feld >= NOW() - wert Einheiten` |
| `olderThenXMinutes` / `olderThenXHours` | `feld + wert Einheiten < NOW()` |

Andere Operatoren (z. B. `in`, `>`, `<`) lehnt der Parser mit dem Fehler `OperatorNotAllowedInFetchXml` ab. `>` und `<` lassen sich mit `geq`/`leq` und dem nächsten Wert nachbilden. Für `in` kannst du mehrere `eq`-Bedingungen in einem `OR`-Filter verwenden.

## Anlegen (`insert`)

```xml
<restapi type="insert">
    <table name="dummy"/>
    <fields>
        <field name="id" value="990001"/>
        <field name="name" value="fx-doc-test"/>
        <field name="Port"><value>4711</value></field>
    </fields>
</restapi>
```

- **Wert angeben:** entweder als Attribut `value` oder als Kindelement `<value>`. Das Kindelement eignet sich für längere Texte.
- **NULL:** Die Werte `""`, `"None"` und `"null"` werden als `NULL` gespeichert. Fehlt `value` ganz, wird ebenfalls `NULL` gespeichert.
- **Primärschlüssel:** Hat die Tabelle kein `auto_increment`, muss das Feld `id` mitgegeben werden. Sonst meldet MariaDB `Field 'id' doesn't have a default value`.
- **Antwort:** `/api/v1.0/data` liefert bei `insert`, `update` und `delete` eine leere Liste `[]`. Brauchst du die neue ID, verwende `POST /api/v1.0/data/<table>` mit einem JSON-Body. Dieser Endpunkt baut intern dieselbe FetchXML und antwortet mit `{"rows_affected": ..., "inserted_id": ...}`.
- **Datensatzrechte:** Ist `enable_record_permission` aktiv, bekommt der anlegende Benutzer automatisch ein Datensatzrecht.

## Ändern (`update`)

```xml
<restapi type="update">
    <table name="dummy"/>
    <fields>
        <field name="Port" value="4712"/>
    </fields>
    <filter>
        <condition field="id" value="990002"/>
    </filter>
</restapi>
```

- **Nur angegebene Felder:** Es werden nur die Felder aus `<fields>` geändert, und zwar in **allen** Datensätzen, auf die der Filter passt.
- **Filter ist Pflicht:** Ohne `<filter>` entsteht `UPDATE ... WHERE` ohne Bedingung, und MariaDB lehnt das mit einem Syntaxfehler ab. Eine ganze Tabelle lässt sich so also nicht versehentlich ändern.
- **Audit-Log:** Ist `enable_audit_log` für die Tabelle aktiv, wird pro geändertem Feld der alte und der neue Wert protokolliert.

## Löschen (`delete`)

```xml
<restapi type="delete">
    <table name="dummy"/>
    <filter>
        <condition field="name" value="fx-doc-test"/>
    </filter>
</restapi>
```

Es löscht alle Datensätze, auf die der Filter passt. Wie bei `update` ist der Filter Pflicht.

## Verwendung in Python (Plugins und Services)

Plugins dürfen kein SQL direkt ausführen. Der vorgesehene Weg für Datenzugriffe ist `FetchXmlParser` zusammen mit `DatabaseServices.exec`:

```python
from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices

def execute(context, plugin_context, params):
    xml=f"""
    <restapi type="select">
        <table name="dummy"/>
        <filter>
            <condition field="Port" operator="geq" value="4711"/>
        </filter>
    </restapi>
    """
    fetch=FetchXmlParser(xml, context)
    rs=DatabaseServices.exec(fetch, context, fetch_mode=0)
    for row in rs.get_result():
        ...
```

- **`fetch_mode=0`:** liest alle Treffer in `rs.get_result()`.
- **`run_as_system=True`:** überspringt die Prüfung der Tabellenrechte (siehe `plugins/api_clear_session.py`).
- **Werte aus Variablen nicht ungeprüft in das XML einsetzen:** Ein `"` oder `<` im Wert zerstört das XML. Escape solche Werte, z. B. mit `xml.sax.saxutils.quoteattr()`, oder baue die FetchXML mit `ElementTree` auf (wie `mcpservice.py`).
- **Transaktion:** Änderungen werden nicht sofort committet. Commit (oder Rollback) erfolgt über den Context, bei HTTP-Requests am Ende des Requests (`teardown_request`).

## Rechte und automatische Bedingungen

- **Tabellenrechte:** Vor der Ausführung prüft `Permission.validate` für jede Tabelle (Haupttabelle und Joins) das passende Recht aus `api_group_permission`: `mode_read`, `mode_create`, `mode_update` oder `mode_delete`. Fehlt es, kommt HTTP 400 mit `no permission (...) for <user> on <table>`.
- **Datensatzrechte:** Ist für die Tabelle `enable_record_permission` aktiv, wird die Bedingung `api_fn_rec_permission(...)` automatisch an `WHERE` angehängt.
- **Gelesen-Markierung:** Jedes `select` blendet Datensätze aus, die in `api_record_meta` mit `meta_type_id=1001` markiert sind (`sys_row_id NOT IN (...)`).
- **Plugins:** Vor und nach der Ausführung laufen die Plugins aus `api_event_handler` mit `publisher=<table-alias>` und `event=<type>` (`before`/`after`).

## Fehler

`/api/v1.0/data` antwortet mit HTTP 400 bei fehlenden Rechten. Alle anderen Fehler kommen als HTTP 500 mit `{"message": "..."}`, zum Beispiel:

| Meldung | Ursache |
|---|---|
| `Table not found for alias: ...` | `<table name>` oder `<join table>` steht nicht in `api_table.alias` |
| `Table: ... on field: ...` | Feld in `<select>` fehlt in `api_table_field` |
| `in` (nur der Operatorname) | Operator nicht erlaubt |
| `Special Chars in String: ;` | `;`, `--`, Tabulator oder Zeilenumbruch in Feldname, Alias, Join-Bedingung oder Kommentar |
| `No Type in xml ...` | `type` fehlt |
| `unknown type in fetchxml: ...` | `type` ist ungültig |
| `(1064, "You have an error in your SQL syntax ...")` | z. B. `update` oder `delete` ohne Filter |

## Hinweise

- **`type`:** `read` wird wie `select` und `create` wie `insert` ausgeführt. Plugins werden aber mit dem Wert aus dem XML ausgelöst. Ein Plugin für `insert` reagiert also nicht auf `type="create"`. Verwende deshalb immer `select`, `insert`, `update` und `delete`.
- **Feldnamen:** In `<filter>` und `<fields>` werden Feldnamen nicht gegen die Metadaten geprüft, nur auf Sonderzeichen. Ein falscher Name fällt erst als SQL-Fehler auf.
- **XML-Sonderzeichen:** `&`, `<` und `"` in Werten müssen XML-escaped werden (`&amp;`, `&lt;`, `&quot;`).
- **`if_condition_func`:** In `<select>` nicht verwenden. Der Code ruft eine Methode `_excape_string` auf, die es nicht gibt, deshalb bricht die Abfrage mit einem Fehler ab. `if_condition_field` und `if_condition_value` ohne `if_condition_func` funktionieren.
