# uWSGI mit Threads, lazy-apps und harakiri

Branch: `features/uwsgi-threads` (Basis: `master`), Stand 20.11.2026

## Ausgangslage

Die von `install.sh` erzeugte `/etc/restapi/uwsgi.<instance>.ini` hatte nur `processes = 10`, ohne Threads, ohne Zeitlimit und ohne Worker-Recycling. Bei der Server-Überlast am 20.11.2026 lief die produktive Instanz mit 50 Prozessen (von Hand geändert). Hängende Requests haben die Worker dauerhaft blockiert, bis uWSGI keine Verbindungen mehr angenommen hat.

Voraussetzungen für Threads, die vorher geprüft wurden:

- **Ein Context und eine DB-Verbindung pro Request** (Branch `features/db-connection-reuse`, bereits in `master`). Keine globale Verbindung, `flask.g` und `session` sind pro Thread getrennt.
- **Geteilte Klassenvariablen** (`AppInfo._current_config`, `JinjaEnvironment._template_functions` / `_filters`) werden nur beim Start geschrieben und danach nur gelesen.
- **`$app_start`-Handler:** `iot_app_start` registriert nur Jinja-Funktionen und zwei Endpunkte (`/iot/v1.0/device/...`), synchron (`run_async=0`). Die importierten Module (`iot_common`, `iot_endpoint_device`, `iot_action_*`) haben beim Import keine Nebenwirkungen: keine DB-, MQTT- oder HTTP-Verbindungen, keine Threads. `tuxlog_app_start` tut nichts (Registrierungen auskommentiert).

## Änderungen

### `install.sh`

Die uWSGI-Vorlage enthält jetzt:

```ini
master = true
processes = $UWSGI_PROCESSES        # Vorgabe 4
threads = $UWSGI_THREADS            # Vorgabe 4
enable-threads = true
thunder-lock = true
lazy-apps = true

harakiri = $UWSGI_HARAKIRI          # Vorgabe 60
harakiri-verbose = true
max-requests = $UWSGI_MAX_REQUESTS  # Vorgabe 2000
reload-on-rss = $UWSGI_RELOAD_ON_RSS  # Vorgabe 300 (MB)
listen = $UWSGI_LISTEN              # Vorgabe 1024
```

| Option | Wirkung |
|---|---|
| `threads` | Threads pro Prozess. `processes × threads` = maximale Zahl paralleler Requests und damit auch ungefähr der DB-Verbindungen |
| `enable-threads` | Nötig für Threads und für Plugins mit `run_async=1` (`AsyncWrapper`). Ohne diese Option laufen Python-Threads in einem uWSGI-Worker nicht zuverlässig |
| `thunder-lock` | Verteilt neue Verbindungen sauber auf Prozesse und Threads |
| `lazy-apps` | Jeder Worker lädt `restapi.py` selbst, statt einmal im Master vor dem `fork()`. Kein Worker erbt dadurch einen DB-Socket. `$app_start` läuft einmal pro Worker und bei jedem Worker-Neustart erneut, damit registriert jeder Worker seine Endpunkte selbst |
| `harakiri` | Bricht Requests ab, die länger als n Sekunden laufen, und startet den Worker neu |
| `max-requests` / `reload-on-rss` | Startet Worker nach n Requests bzw. ab n MB Speicher neu (gegen Speicherlecks) |
| `listen` | Länge der Warteschlange für neue Verbindungen (`net.core.somaxconn` muss mindestens so groß sein, unter Debian 12 ist der Standard 4096) |

### `config.py` / `config.skelet`

Neuer optionaler Abschnitt `uwsgi`. Fehlt er oder ein Schlüssel, gelten die Vorgaben oben:

```python
"uwsgi": {"processes":4, "threads":4, "harakiri":60, "max_requests":2000, "reload_on_rss":300, "listen":1024},
```

Bestehende `config.py`-Dateien müssen nicht angepasst werden.

### `cfgreader.py`

Optionales drittes Argument als Vorgabewert: `cfgreader.py <section> <key> [<default>]`. Ohne Vorgabe bricht ein fehlender Schlüssel wie bisher mit einem Fehler ab.

## Tests

Getestet mit der aus `install.sh` erzeugten `.ini` (Port und `uid`/`gid` für den Test geändert) gegen die Dev-Datenbank `tuxlog_staging`. Dort sind `iot_app_start` und `tuxlog_app_start` aktiv. Maschine mit 4 Kernen, uWSGI 2.0.31.

**Endpunkte nach Worker-Neustart** (`max-requests = 20`, 600 Requests, 30 parallel, gemischt aus IoT-Endpunkt, username/password und Gast):

- Es gab 12 Worker-Neustarts und 16 App-Ladevorgänge.
- Der IoT-Endpunkt `/iot/v1.0/device/x/1/on` antwortete bei allen 200 Requests mit 400 (Gerät existiert nicht), nie mit 405. Ein nicht registrierter Pfad landet beim Portal-Catch-all mit 405. Die Route war also nach jedem Neustart vorhanden.
- Alle Requests mit username/password lieferten 200 mit dem richtigen Datensatz.
- Keine Meldungen `InterfaceError`, `Commands out of sync`, `Packet sequence number wrong` oder Tracebacks im Log.

**Durchsatz** (`ab -n 600 -c 30`, username/password, `max-requests = 2000`):

| Konfiguration | Requests/s | längster Request | Fehler | DB-Verbindungen |
|---|---|---|---|---|
| 4 Prozesse × 4 Threads | 28,0 | 1,4 s | 0 | 606 |
| 4 Prozesse × 1 Thread | 29,9 | 1,2 s | 0 | 607 |
| 10 Prozesse × 1 Thread (bisher) | 29,2 | 1,4 s | 0 | 603 |

Bewertung:

- **Durchsatz:** Er ist in allen drei Fällen gleich. Die Requests in diesem Test sind durch die CPU begrenzt, 4 Prozesse lasten die 4 Kerne bereits aus. Threads bringen hier keinen Durchsatz, schaden aber auch nicht.
- **Wann Threads helfen:** wenn Requests auf etwas warten, zum Beispiel eine langsame DB oder ein Plugin, das per HTTP oder MQTT ein Gerät schaltet. Dann blockiert ein Request nur einen Thread statt eines ganzen Prozesses.
- **Speicher:** Der größte Gewinn gegenüber dem Server ist, dass 4 Prozesse statt 50 laufen.
- **Verbindungen:** Weiterhin 1 DB-Verbindung pro Request.

## Deployment auf dem Server

`install.sh` ist so ausgelegt, dass es mehrfach laufen kann. Die `.ini` wird damit neu erzeugt:

1. Branch auschecken:
   ```bash
   git fetch origin
   git switch features/uwsgi-threads
   ```
2. Die alte `.ini` für einen Rollback sichern:
   ```bash
   sudo cp /etc/restapi/uwsgi.<instance>.ini /etc/restapi/uwsgi.<instance>.ini.bak
   ```
3. Optional den Abschnitt `uwsgi` in `config.py` ergänzen, wenn andere Werte als die Vorgaben gelten sollen. Von Hand geänderte Werte in der `.ini`, zum Beispiel `processes = 50`, überschreibt `install.sh`.
4. `install.sh` ausführen:
   ```bash
   ./install.sh <restapi_user> <restapi_password>
   ```
5. Dienste neu starten (`install.sh` lädt nur `systemctl daemon-reload`):
   ```bash
   ./services.sh restart
   ```
6. Prüfen:
   - `journalctl -u restapi.<instance>.service` meldet `python threads support enabled` und `cores: 4` pro Worker.
   - Die IoT-Endpunkte und das UI funktionieren.
   - Kein `HARAKIRI ON WORKER` im Log. Wenn doch, ist der betroffene Request zu langsam oder `harakiri` zu klein.

Der `timeout=` im Apache-`ProxyPass` sollte etwas größer als `harakiri` sein, zum Beispiel `timeout=70` bei `harakiri = 60`. Sonst bricht Apache zuerst ab, während der Worker weiterrechnet.

**Rollback:**

```bash
sudo cp /etc/restapi/uwsgi.<instance>.ini.bak /etc/restapi/uwsgi.<instance>.ini
./services.sh restart
```

Am Python-Code der restapi ändert sich nichts. Es bleibt deshalb egal, ob dabei `master` oder dieser Branch ausgecheckt ist. Ein späterer Lauf von `install.sh` auf `master` erzeugt allerdings wieder die alte `.ini`.

## Hinweise

- **Hinweis von uWSGI beim Start:** `you have enabled harakiri without post buffering`. Das betrifft nur sehr langsame Uploads, die dadurch abgebrochen werden können. Bei Bedarf hilft `post-buffering = 8192`.
- **`$app_start`:** Kommt später ein Handler mit Nebenwirkungen dazu (DB schreiben, MQTT verbinden, Threads starten), läuft dieser einmal pro Worker und bei jedem Worker-Neustart erneut.
