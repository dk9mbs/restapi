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
| `inline_code` | Python-Code für das Plugin `api_exec_inline_code` (siehe [Inline-Code](#inline-code)) |

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

## Inline-Code

Kleine Logik kann direkt in `api_event_handler.inline_code` stehen, ohne eigenes Modul. Dafür trägst du als `plugin_module_name` das Plugin `api_exec_inline_code` ein. Es führt den Code aus `inline_code` aus. Alle anderen Spalten (`publisher`, `event`, `type`, `run_async`, ...) gelten wie bei jedem Plugin. Im UI hat das Feld einen Python-Editor.

Im Code verfügbar sind `params`, `context`, `plugin_context`, `print` und `dir`.

Beispiel für `publisher=<tabelle>`, `event=insert`, `type=before`, das ein Rufzeichen vor dem Speichern in Großbuchstaben umwandelt:

```python
if 'call' in params['data'] and params['data']['call']['value']:
    params['data']['call']['value']=params['data']['call']['value'].strip().upper()
```

- **Funktionen:** Eine im Inline-Code definierte Funktion sieht `context` und `plugin_context` nicht. Übergib sie als Parameter, z. B. `def check(context, data): ...` und `check(context, params['data'])`.
- **Fehler:** `api_exec_inline_code` hat `raise_exception: True`. Ein Fehler im Code bricht den auslösenden Vorgang ab, z. B. das Speichern des Datensatzes.
- **Ausgaben:** `print()` schreibt in das Log des Dienstes (`journalctl -u restapi.<instance>.service`).
- **Gleiche Regeln:** Für Inline-Code gilt alles aus diesem Leitfaden, auch kein direktes SQL und das Escapen von Werten in FetchXML.
- **Wann ein Modul besser ist:** Sobald der Code länger als ein paar Zeilen ist, getestet werden soll oder zu einer Lösung gehört. Ein Modul liegt in Git und lässt sich mit der Lösung ausrollen, Inline-Code nur als Datensatz.
- **Rechte:** Inline-Code läuft wie Plugin-Code im Serverprozess. Schreibrecht auf `api_event_handler` gehört deshalb nur Administratoren.

## Eigene Endpunkte

Ein `$app_start`-Plugin kann eigene Endpunkte registrieren (`AppInfo.get_api("solution").add_resource(...)`). Für diese Endpunkte gilt alles oben Gesagte. Zusätzlich:

- **Anmeldung:** Die Anmeldung erledigt `before_request`, der Benutzer steht in `g.context`. Die Rechte prüft der Endpunkt selbst.
- **Werte aus URL und Query:** Pfad- und Query-Parameter sind Eingaben wie alle anderen. Prüfe und escape sie.
- **Fehlermeldungen:** Mit `abort(400, ...)` für falsche Eingaben und `abort(500, ...)` für Fehler antworten. Keine Tracebacks und keine internen Details an den Client geben.

## Plugins in einer eigenen Lösung

Wie Plugins zusammen mit Tabellen, Metadaten und Templates als eigene Lösung (z. B. IoTSensorNet, tuxlog) importiert werden, steht in [solutions.md](solutions.md).

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
- [ ] Inline-Code nur für kurze Logik, Schreibrecht auf `api_event_handler` nur für Administratoren
- [ ] Bei einer eigenen Lösung: die Checkliste in [solutions.md](solutions.md)
