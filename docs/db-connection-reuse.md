# Eine DB-Verbindung pro Request

Branch: `features/db-connection-reuse` (Basis: `master`), Stand 20.11.2026

## Ausgangslage

Bisher hat die restapi pro HTTP-Request mehrere Verbindungen zur MariaDB geöffnet und wieder geschlossen. Jeder Schritt hatte eine eigene Verbindung:

| Schritt | Verbindung |
|---|---|
| `guest_credentials()` / `user_credentials_by_apikey()` | eigene |
| `login()` | eigene |
| `create_context()`: Session und User lesen | eigene |
| `create_context()`: Context-Verbindung für den Request | eigene |
| `save_context()` bzw. `logoff()` in `teardown_request` | eigene |

Ergebnis: 3 bis 5 Verbindungsaufbauten pro Request (TCP, Authentifizierung, Session-Setup). Bei vielen pollenden Clients (siehe Server-Überlast am 20.11.2026) erzeugt das unnötig Last auf der Datenbank. Außerdem blieb bei `login()` mit falschem Passwort die Verbindung offen (Leak).

## Lösung

Alle Schritte eines Requests nutzen dieselbe Verbindung. Sie wird einmal geöffnet und ist danach die Verbindung des `Context`.

### `core/appinfo.py`

- **`create_context(session_id, auto_logoff=False, auto_commit=False, connection=None)`**
  - Nutzt die übergebene Verbindung oder öffnet eine neue.
  - Liest Session und User und beendet die Lesetransaktion mit `commit()`, damit der Request aktuelle Daten sieht.
  - Die Verbindung wird zur Context-Verbindung, es wird keine zweite mehr geöffnet.
  - Bei einem Fehler (z. B. `NameError` „Session not exists“) wird die Verbindung geschlossen. Der Aufrufer darf sie danach nicht mehr verwenden.
- **`save_context(context, close_context=True)`**: Das `UPDATE api_session` läuft auf der Context-Verbindung, solange sie offen ist. Anschließend `context.close()` bzw. `context.commit()`. Ist die Verbindung bereits geschlossen, wird wie bisher eine eigene geöffnet.
- **`logoff(context)`**: `DELETE FROM api_session` auf der Context-Verbindung, solange sie offen ist, sonst auf einer eigenen.
- **`login(username, password, connection=None)`**: Mit übergebener Verbindung wird nur committet, nicht geschlossen. Ohne Verbindung wird eine eigene geöffnet und in `finally` geschlossen (behebt den Leak bei falschem Passwort).
- **`guest_credentials()`, `system_credentials()`, `user_credentials_by_apikey()`**: optionaler Parameter `connection`. Gemeinsame Hilfsfunktion `_fetch_one(sql, params, connection=None)`.
- Neue Hilfsfunktion **`_open_context_connection(context)`**: liefert die Context-Verbindung, wenn sie offen ist, sonst `None`.

### `restapi.py` (`before_request`)

Im Block ohne Cookie/JWT (`if not login:`) wird eine Verbindung geöffnet und an Credential-Abfrage, `login()` und `create_context()` übergeben. Bei einem Fehler (auch `abort(400)`) wird sie geschlossen.

### `api/core/login.py`

`POST /v1.0/core/login` nutzt eine Verbindung für `login()` und `create_context()`. Bei falschen Zugangsdaten wird sie geschlossen.

### Abwärtskompatibilität

Alle neuen Parameter sind optional. Aufrufer, die nichts übergeben (`timerservice.py`, `msgservice.py`, `core/plugin.py`, `tools/metadata.py`, Plugins, Tests), verhalten sich wie bisher. Am DB-Schema und an den Daten ändert sich nichts.

## Tests

### Unit-Tests

Neu: `test/test_appinfo_connection.py`. Der Test zählt über `mock.patch.object(AppInfo, 'create_connection', side_effect=...)` die geöffneten Verbindungen:

| Test | Prüft |
|---|---|
| `test_000_request_with_login` | Gast-Login + Context + Logoff mit genau 1 Verbindung, Session danach gelöscht |
| `test_001_request_with_session` | Request mit vorhandener Session: 1 Verbindung, Session-Werte gespeichert, Logoff nach geschlossenem Context |
| `test_002_save_context_without_close` | `save_context(close_context=False)` lässt die Verbindung offen |
| `test_003_wrong_password` | Falsches Passwort: übergebene Verbindung bleibt offen, ohne Verbindung liefert `login()` `None` |
| `test_004_unknown_session_closes_connection` | Unbekannte Session schließt die übergebene Verbindung |
| `test_005_credentials_without_connection` | Credential-Abfragen ohne Verbindung |

```bash
. ./init.sh
python -m unittest discover -v -s test
```

Ergebnis: 75 von 76 Tests bestanden. `test_xml_reader` schlägt auch auf `master` fehl (`escm_message_exchange` fehlt in `shared/model.py`). Die neuen Tests schlagen auf `master` fehl.

### Messung auf der Dev-Instanz

Je 20 Requests, gezählt mit `SHOW GLOBAL STATUS LIKE 'Connections'`, Verbindungen pro Request:

| Login-Art | master | Branch |
|---|---|---|
| Gast (anonym) | 5 | **1** |
| apikey | 5 | **1** |
| username/password | 4 | **1** |
| `POST /v1.0/core/login` | 4 | **1** |
| Session-Cookie | 3 | **1** |
| JWT Bearer | 3 | **1** |
| falsches Passwort | 1 | 1 |

Die HTTP-Statuscodes sind auf beiden Ständen gleich.

## Deployment und Rollback

```bash
git fetch origin
git switch features/db-connection-reuse
sudo systemctl restart restapi.<instance>.service restapi-timer.<instance>.service restapi-msg.<instance>.service
```

Alle drei Dienste neu starten, weil auch Timer- und Msg-Service `AppInfo` nutzen. uWSGI lädt geänderten Code nicht automatisch.

Beobachten:
- Apache-`error.log` und `journalctl -u restapi.<instance>.service`
- `SHOW GLOBAL STATUS LIKE 'Connections'` sollte deutlich langsamer steigen
- Timer- und Msg-Plugins laufen weiter (`api_process_log`)

Rollback: `git switch master` und dieselben Restart-Befehle. Ohne Schemaänderung ist das unkritisch.

## Offen

- **`api_session`-Wachstum:** Clients mit username/password oder apikey ohne Cookie legen weiterhin pro Request eine neue Session-Zeile an (bei 20 Requests 20 Zeilen). Das ist nicht Teil dieser Änderung.
- **Connection-Pool / Wiederverwendung über Requests hinweg** ist ebenfalls nicht Teil dieser Änderung.
