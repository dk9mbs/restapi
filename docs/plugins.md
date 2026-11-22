# Plugins schreiben

Leitfaden für Plugins in der restapi und in den Zusatzmodulen (IoTSensorNet, tuxlog, restapi.bank, ...). Er beschreibt, wie Plugins aufgerufen werden und worauf du beim Schreiben achten solltest.

## Aufbau

Ein Plugin ist ein Python-Modul mit einer Funktion `execute()` und optional einer Funktion `config()`:

```python
from core import log

logger=log.create_logger(__name__)

def config():
    return {"raise_exception": False}

def execute(context, plugin_context, params):
    ...
```

| Parameter | Inhalt |
|---|---|
| `context` | `Context` mit DB-Verbindung, Benutzer, Session und Request-Argumenten |
| `plugin_context` | Infos zum Aufruf: `publisher`, `trigger`, `type`, `process_id`, `config` (JSON aus `api_event_handler.config`) und `response` |
| `params` | Die Daten des Ereignisses (siehe unten) |

Registriert wird ein Plugin über eine Zeile in `api_event_handler`:

| Spalte | Bedeutung |
|---|---|
| `plugin_module_name` | Modulname, z. B. `iot_app_start`. Das Modul muss im `PYTHONPATH` liegen (`plugins/` oder `plugin.root` aus `config.py`) |
| `publisher`, `event` | Wann das Plugin läuft (siehe nächster Abschnitt) |
| `type` | `before` oder `after` |
| `run_async` | `0` synchron im Request, `-1` in einem eigenen Thread |
| `run_queue` | `-1`: asynchron über die Warteschlange des Timer-Dienstes statt in einem Thread |
| `is_single_instance` | `-1`: läuft nicht parallel ein zweites Mal |
| `sorting` | Reihenfolge, wenn mehrere Plugins auf dasselbe Ereignis reagieren |
| `is_enabled` | `-1` aktiv, `0` aus |
| `config` | JSON, das im Plugin als `plugin_context['config']` ankommt |

Präfixe im Dateinamen zeigen die Zugehörigkeit (`api_*`, `iot_*`, `tuxlog_*`, `bank_*`, ...). Wähle eindeutige Modulnamen, denn alle Plugin-Verzeichnisse liegen im selben `PYTHONPATH`.

## Ereignisse und `params`

| Ereignis | `publisher` / `event` | `params` |
|---|---|---|
| Tabellenänderung | Tabellen-Alias / `insert`, `update`, `delete` | `{"data": {"<feld>": {"value": ..., "old_value": ...}}}` |
| Lesen einer Tabelle | Tabellen-Alias / `select` | `before`: leer, `after`: `{"data": [<datensätze>]}` |
| Aktion | `<action>` / `execute` (`type=before`) | `{"input": <JSON-Body>, "output": {}}`. `output` ist die HTTP-Antwort von `POST /api/v1.0/action/<action>` |
| Timer | `$timer_every_minute`, `$timer_every_ten_minutes`, `$timer_every_hour`, `$timer_every_day` / `execute` | `{"input": {}, "output": {}}` |
| MQTT-Nachricht | Topic-Publisher / `mqtt_message` | `{"data": <Payload>, "topic": "<topic>"}` |
| Start der App | `$app_start` / `execute` | leer |

- **Bei Tabellenänderungen mit `before`:** Das Plugin kann Werte in `params['data']` ändern, bevor sie gespeichert werden.
- **Bei `select` mit `after`:** Das Plugin kann die gelesenen Datensätze ändern oder ergänzen.

## Daten lesen und schreiben

**Kein SQL direkt im Plugin.** Die Schichten sind Plugins → `services/` → `core/`. Für Daten nimmst du `DatabaseServices.exec()` mit `FetchXmlParser`, `FetchSqlParser` oder dem ORM. Für Systemfunktionen (Rechte, Metadaten) nimmst du die passenden Funktionen aus `core/`. Fehlt dort eine Funktion, gehört sie zuerst nach `core/`.

Details zu FetchXML stehen in [fetchxml.md](fetchxml.md).

### Werte in FetchXML immer escapen

Jeder Wert, der nicht fest im Code steht, kommt durch `escape_xml_value()` in die FetchXML. Das gilt für Werte aus `params`, aus HTTP-Requests, von Geräten, aus MQTT, aus der Datenbank und aus Variablen:

```python
import datetime
from core.fetchxmlparser import FetchXmlParser, escape_xml_value
from services.database import DatabaseServices

def execute(context, plugin_context, params):
    node_name=params['input'].get('node_name')
    now=datetime.datetime.now()

    xml=f"""
    <restapi type="update">
        <table name="iot_node"/>
        <fields>
            <field name="last_heard_on" value="{escape_xml_value(now)}"/>
        </fields>
        <filter>
            <condition field="name" value="{escape_xml_value(node_name)}"/>
        </filter>
    </restapi>
    """
    DatabaseServices.exec(FetchXmlParser(xml, context), context)
```

Warum das nötig ist: Ein unescapter Wert mit `"` oder `>` verändert die Struktur des XML. Daraus kann eine gültige, aber ganz andere Abfrage werden, zum Beispiel mit einem anderen Filter oder mit zusätzlichen Feldern. Der Parser kann das nicht erkennen, weil nur erlaubte Bausteine vorkommen.

Alternativ baust du die FetchXML mit `xml.etree.ElementTree` auf. Dann übernimmt `ElementTree` das Escaping.

**Feld- und Tabellennamen** dürfen nicht aus Eingaben stammen. Muss das doch sein, prüfe den Namen gegen eine feste Liste erlaubter Namen.

### Rechte

- **`run_as_system=True` umgeht die Tabellenrechte.** Verwende es nur, wenn das Plugin wirklich Daten lesen oder schreiben muss, die der aufrufende Benutzer nicht sehen darf. Prüfe die Eingaben dann besonders sorgfältig.
- **Aktionen:** `POST /api/v1.0/action/<action>` führt das Plugin für jeden Aufrufer aus. Anfragen ohne Anmeldung laufen als Benutzer `guest`. Ob der Aufrufer die Aktion ausführen darf, muss das Plugin selbst entscheiden. Möglich sind die Tabellenrechte (`DatabaseServices.exec` ohne `run_as_system`) oder `core/permission.py`, zum Beispiel `Permission().is_admin(context, context.get_username())`.
- **Asynchrone Plugins** (`run_async=-1`) laufen mit einem eigenen Context als Benutzer `system`, nicht als aufrufender Benutzer.

## Eingaben prüfen

Alles in `params` kommt potenziell von außen: HTTP-Body, Query-Parameter, Geräte, MQTT.

- **Pflichtfelder:** Fehlende Pflichtfelder sofort mit einer klaren Fehlermeldung abweisen.
- **Typen und Wertebereiche:** Prüfen, zum Beispiel mit `int()`, `float()` oder einem regulären Ausdruck. Für Aktionen, die als MCP-Tool freigegeben sind, gibt `input_schema` in `api_mcp_tool` das Format vor. Prüfe trotzdem im Plugin.
- **Längen begrenzen:** besonders bei Texten, die gespeichert oder weitergeschickt werden.
- **Kein `eval()` oder `exec()`** und kein `subprocess` mit Werten aus `params`.
- **Pfade:** Dateipfade aus Eingaben gegen ein festes Basisverzeichnis prüfen (kein `..`).
- **URLs:** Für ausgehende Requests keine frei wählbaren URLs aus Eingaben verwenden. Nimm feste Hosts aus der Konfiguration.

## Zugangsdaten und Konfiguration

- **Keine Passwörter, Tokens oder API-Keys im Code.** Lege sie in `api_setting` ab (`Setting.get_value(context, "<name>", default)`) oder in `api_event_handler.config`.
- **Keine Geheimnisse in `params` und im Log.** Der Inhalt von `params` wird beim Start jedes Plugin-Laufs als `request_msg` in `api_process_log` gespeichert. Auch `logger.info(...)` schreibt ins Journal.
- **HTTPS:** Bei ausgehenden HTTPS-Requests das Zertifikat prüfen (`verify=True`, Vorgabe bei `requests`).

## Fehlerbehandlung und Transaktionen

- **Fehler werden protokolliert:** Eine Exception im Plugin wird geloggt und in `api_process_log` mit `status_id=20` und `error_text` gespeichert.
- **Fehler weitergeben:** Mit `config()` → `{"raise_exception": True}` wird die Exception zusätzlich weitergereicht. Bei synchronen Plugins bricht der Request dann ab. So verhindert zum Beispiel ein `before`-Plugin ein ungültiges `insert`.
- **Status melden:** Setze `plugin_context['response']['status_code']`, `payload` und `error_text`, wenn das Plugin einen eigenen Status melden soll. Ein `status_code` außer `0` und `200` gilt als Fehler.
- **Kein automatischer Rollback:** Gehe nicht davon aus, dass Änderungen bei einem Fehler zurückgerollt werden. Das Protokoll eines Plugin-Laufs wird sofort committet, und dabei auch alles, was bis dahin auf derselben Verbindung geschrieben wurde. Prüfe deshalb zuerst und schreibe erst danach. Halte Änderungen, die zusammengehören, möglichst in einer Anweisung zusammen.
- **Kein eigener Commit:** Rufe `context.commit()` nicht selbst auf. Das übernehmen der Request (`teardown_request`) bzw. der asynchrone Wrapper.

## Laufzeit

- **Zeitlimit:** uWSGI bricht Requests nach `harakiri` Sekunden ab (Vorgabe 60). Synchrone Plugins müssen deutlich schneller fertig sein.
- **Lange Arbeiten** gehören in ein asynchrones Plugin (`run_async=-1`) oder in die Warteschlange (`run_queue=-1`).
- **Timeouts:** Jeder ausgehende Request braucht einen Timeout, z. B. `requests.get(url, timeout=10)`. Das gilt auch für MQTT und andere Netzwerkzugriffe.
- **Timer-Plugins** laufen regelmäßig. Sie sollten nur die Daten anfassen, die seit dem letzten Lauf neu sind, zum Beispiel über einen Filter mit `lastXminutes`.

## Threads, Prozesse und Modul-Code

Die restapi läuft unter uWSGI mit mehreren Prozessen und Threads (`lazy-apps`). Daraus folgt:

- **Beim Import nichts ausführen:** Code auf Modulebene läuft beim Import einmal pro Worker-Prozess und bei jedem Neustart eines Workers erneut. Dort nur Konstanten, Funktionen, Klassen und Logger anlegen. Keine DB-, MQTT- oder HTTP-Verbindungen öffnen, keine Threads starten.
- **Kein gemeinsamer Zustand:** Kein veränderlicher Zustand auf Modulebene (globale Dicts, Listen, Caches, Verbindungen). Mehrere Threads führen das Plugin gleichzeitig aus. Zustand gehört in die Datenbank oder in den `context`.
- **Kein `flask.g` oder `request`:** Verwende die DB-Verbindung immer über den übergebenen `context`, nie über `flask.g` oder `flask.request`. Asynchrone Plugins und Timer laufen außerhalb eines HTTP-Requests.
- **`$app_start`-Plugins** laufen in jedem Worker. Sie sollen nur registrieren (Endpunkte, Jinja-Funktionen) und müssen mehrfaches Ausführen vertragen. Sie müssen synchron laufen (`run_async=0`), damit die Endpunkte vor dem ersten Request bereitstehen.

## Eigene Endpunkte

Ein `$app_start`-Plugin kann eigene Endpunkte registrieren (`AppInfo.get_api("solution").add_resource(...)`). Für diese Endpunkte gilt alles oben Gesagte. Zusätzlich:

- **Anmeldung:** Die Anmeldung erledigt `before_request`, der Benutzer steht in `g.context`. Die Rechte prüft der Endpunkt selbst.
- **Werte aus URL und Query:** Pfad- und Query-Parameter sind Eingaben wie alle anderen. Prüfe und escape sie.
- **Fehlermeldungen:** Mit `abort(400, ...)` für falsche Eingaben und `abort(500, ...)` für Fehler antworten. Keine Tracebacks und keine internen Details an den Client geben.

## Plugins in einer eigenen Lösung (Zusatzmodul)

Eigene Lösungen wie IoTSensorNet oder tuxlog liegen in einem eigenen Repository. Sie werden mit `tools/solution.py` in eine restapi-Instanz importiert.

### Aufbau des Lösungsordners

```
<repo>/restapi/
    solution.json        Pflicht: ID und Name der Lösung (siehe IoTSensorNet/restapi/solution.json)
    database/install.sql Tabellen, Metadaten, Plugin-Registrierung, Views, Menüs
    plugins/             Plugin-Module (nur Dateien, keine Unterordner)
    wwwroot/             Templates und statische Dateien
```

`solution.py` verarbeitet nur `database/install.sql`, `plugins/` und `wwwroot/`. Andere Ordner im Lösungsordner (z. B. `tools/`, `test/`, `docs/`) werden nicht kopiert.

### Import

```bash
cd /pfad/zur/restapi/tools
. ../init.sh
python solution.py -p /pfad/zu/IoTSensorNet/restapi/
```

`solution.py` muss aus dem Verzeichnis `tools/` der restapi aufgerufen werden, denn es ermittelt das restapi-Verzeichnis aus dem aktuellen Verzeichnis. Das Skript macht Folgendes:

1. **Datenbank:** Es führt `database/install.sql` mit dem `mysql`-Client und den Zugangsdaten aus `config.py` aus. Bei einem Fehler bricht es ab.
2. **Plugins:** Es kopiert alle Dateien aus `plugins/` nach `<restapi>/plugins/`.
3. **wwwroot:** Es kopiert `wwwroot/` rekursiv nach `<restapi>/wwwroot/`.

Danach:

```bash
cd /pfad/zur/restapi
python tools/metadata.py -u <restapi_user> -p <restapi_password>   # wenn sich Tabellen oder Felder geändert haben
./services.sh restart
```

- **`tools/metadata.py`** baut den Metadaten-Cache (`api_table_field`) und `shared/model.py` neu auf. Das ist nötig, wenn die Lösung Tabellen oder Felder hinzufügt oder ändert.
- **`./services.sh restart`** ist immer nötig. Jeder Worker lädt ein Plugin-Modul nur einmal, neuer Plugin-Code wird erst nach einem Neustart aktiv. Das gilt auch für den Timer- und den Msg-Dienst.

### Regeln für `database/install.sql`

Das Skript läuft bei jedem Import erneut und muss deshalb mehrfach ausführbar sein:

- **Eigene Zeilen über `solution_id` ersetzen:** Am Anfang die eigenen Zeilen löschen und danach mit `INSERT IGNORE` neu anlegen. Das betrifft die Zeilen aus `api_event_handler`, `api_table_view`, `api_ui_app` und `api_ui_app_nav_item` und die Einträge in `api_process_log`, die zu den eigenen Event-Handlern gehören:
  ```sql
  DELETE FROM api_process_log WHERE event_handler_id IN (SELECT id FROM api_event_handler WHERE solution_id=10000);
  DELETE FROM api_event_handler WHERE solution_id=10000;
  INSERT IGNORE INTO api_solution(id,name) VALUES (10000, 'IoTSensorNet');
  ```
  Lösche nur Zeilen mit der eigenen `solution_id`, niemals Zeilen anderer Lösungen oder der restapi selbst.
- **Tabellen nicht löschen:** Tabellen mit `CREATE TABLE IF NOT EXISTS` anlegen, Spalten und Schlüssel mit `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` bzw. `ADD ... KEY IF NOT EXISTS` ergänzen. Kein `DROP TABLE` und kein `TRUNCATE` auf Tabellen mit Daten.
- **Eigener ID-Bereich:** Vergib IDs in einem eigenen Bereich, z. B. `solution_id` 10000 mit IDs ab `10000001`. So kommen sich Lösungen nicht in die Quere.
- **Metadaten:** Neue Tabellen brauchen eine Zeile in `api_table` (mit `solution_id`) und Rechte in `api_group_permission`. Gib dabei nur die Rechte, die die Gruppen wirklich brauchen. Für `guest` gilt das besonders.
- **Plugins registrieren:** in `api_event_handler` mit `solution_id` (siehe „Aufbau“).

### Regeln für `plugins/`

- **Eindeutige Dateinamen:** Alle Lösungen landen im selben Verzeichnis `<restapi>/plugins/`, und eine Datei mit gleichem Namen wird überschrieben. Verwende deshalb ein Präfix der Lösung (`iot_`, `tuxlog_`, ...).
- **Keine Unterordner:** Lege Hilfsmodule als eigene Dateien mit Präfix an, z. B. `iot_common.py`.
- **Umbenennen oder Löschen:** Entfernt oder umbenannt wird eine Datei nur in der Lösung, nicht in der Instanz. Lösche alte Dateien in `<restapi>/plugins/` von Hand und deaktiviere bzw. entferne die zugehörigen Zeilen in `api_event_handler`.
- **Alternative ohne Kopieren:** `plugin.root` in `config.py` liegt ebenfalls im `PYTHONPATH`. Module dort werden ohne Kopieren gefunden.

### Während des Imports

Zwischen dem Löschen und dem Neuanlegen der eigenen Zeilen in `install.sql` fehlen die Event-Handler der Lösung kurz. Plugins, die in diesem Moment laufen sollten, werden übersprungen. Importiere deshalb möglichst in einer ruhigen Zeit, und starte die Dienste direkt danach neu.

## Checkliste

- [ ] Kein direktes SQL, Datenzugriff über `DatabaseServices.exec()`
- [ ] Alle variablen Werte in FetchXML mit `escape_xml_value()` (oder `ElementTree`)
- [ ] Keine Tabellen- oder Feldnamen aus Eingaben, sonst gegen eine feste Liste geprüft
- [ ] Eingaben auf Pflichtfelder, Typ, Wertebereich und Länge geprüft
- [ ] `run_as_system=True` nur, wo es nötig ist
- [ ] Aktion bzw. eigener Endpunkt prüft, ob der Benutzer die Aktion ausführen darf
- [ ] Keine Zugangsdaten im Code, in `params` oder im Log
- [ ] Timeouts bei allen Netzwerkzugriffen
- [ ] Synchron deutlich unter dem `harakiri`-Limit, sonst asynchron
- [ ] Kein Code mit Nebenwirkungen auf Modulebene, kein globaler veränderlicher Zustand
- [ ] `raise_exception` bewusst gesetzt
- [ ] Bei einer eigenen Lösung: Dateiname mit Präfix, `install.sql` mehrfach ausführbar, nur Zeilen der eigenen `solution_id` gelöscht
