# Spezifikation: Dev-Server-Flag für services.sh

Stand: 2026-11-13

## Ausgangslage

`tools/services.sh` startet, stoppt oder startet immer dieselben vier Units einer Instanz neu: `restapi`, `restapi-msg`, `restapi-mcp` und `restapi-timer`. Die Unit `restapi-dev.<instanz>.service` fehlt, obwohl `install.sh` sie anlegt und am Ende sogar statt `restapi` zum Starten empfiehlt.

| Unit | Startet | Gedacht für |
| --- | --- | --- |
| `restapi.<instanz>.service` | `restapi.py` unter uwsgi | Produktion, Test |
| `restapi-dev.<instanz>.service` | `restapi.py` direkt mit dem Flask-Dev-Server | Entwicklung (standalone) |

Beide Units bedienen dieselbe API. Sie dürfen nicht gleichzeitig laufen.

## Ziel und Nicht-Ziele

Ein neues Flag in `config.py` legt fest, ob eine Instanz ein Entwicklungssystem ist. `services.sh` steuert dann entweder `restapi-dev` oder `restapi`, nie beide.

Nicht Teil dieser Änderung:

- `install.sh` legt weiterhin beide Units an. Das ist so entschieden.
- `enable` und `disable` (Autostart) bleiben außerhalb von `services.sh`.
- `restapi.py` liest das Flag nicht. Es betrifft nur den Betrieb der Units.

## Konfiguration

Das Property `instance` bekommt den Schlüssel `standalone` mit den Werten `0` oder `1`, analog zu `enable_swagger_doc`.

```
"instance": {"id":"dev", "enable_swagger_doc":1, "standalone":1},
```

| Wert | Bedeutung | Gesteuerte API-Unit |
| --- | --- | --- |
| `0` (Default) | Produktions- oder Testsystem | `restapi.<instanz>.service` |
| `1` | Entwicklungssystem | `restapi-dev.<instanz>.service` |

- Fehlt der Schlüssel, gilt `0`. Bestehende `config.py`-Dateien laufen damit ohne Anpassung weiter wie bisher.
- `config.skelet` bekommt `"standalone":0`, damit neue Instanzen das Flag sichtbar enthalten.
- Jeder andere Wert als `0` oder `1` ist ein Fehler: `services.sh` bricht mit Meldung ab, bevor es eine Unit anfasst.

## cfgreader.py

`cfgreader.py` bekommt ein optionales drittes Argument als Default-Wert. Ohne ein solches Argument bricht es heute bei einem fehlenden Schlüssel mit `KeyError` ab.

```
python3 cfgreader.py instance standalone 0
```

- Mit Default: Fehlt der Schlüssel oder die Sektion, gibt das Skript den Default aus und endet mit Exit-Code 0.
- Ohne Default: Verhalten wie bisher. Die bestehenden Aufrufe in `install.sh` und `init.sh` bleiben unverändert.

## Verhalten von tools/services.sh

`services.sh` liest `instance.standalone` mit Default `0` und wählt danach die erste Unit der Liste. Die anderen drei Units bleiben gleich.

| Reihenfolge bei start/restart | `standalone=0` | `standalone=1` |
| --- | --- | --- |
| 1 | `restapi.<instanz>` | `restapi-dev.<instanz>` |
| 2 | `restapi-msg.<instanz>` | `restapi-msg.<instanz>` |
| 3 | `restapi-mcp.<instanz>` | `restapi-mcp.<instanz>` |
| 4 | `restapi-timer.<instanz>` | `restapi-timer.<instanz>` |

- Bei `stop` läuft die Liste wie bisher rückwärts, die API-Unit wird also zuletzt gestoppt.
- Die nicht gewählte API-Unit fasst das Skript nicht an. Läuft sie trotzdem, zum Beispiel nach einem manuellen Start, gibt das Skript vor dem ersten `systemctl`-Aufruf eine Warnung aus und macht weiter.
- Die Kopfzeile zeigt den Modus mit an, zum Beispiel `Instance: dev (standalone)`.

## Abnahmekriterien

- [ ] Mit `standalone=1` startet `tools/services.sh restart` die Unit `restapi-dev` und lässt `restapi` aus.
- [ ] Mit `standalone=0` startet es `restapi` und lässt `restapi-dev` aus.
- [ ] Eine `config.py` ohne `standalone` verhält sich wie `standalone=0`, ohne Fehlermeldung.
- [ ] Ein ungültiger Wert, zum Beispiel `2`, bricht vor dem ersten `systemctl`-Aufruf mit Exit-Code 1 ab.
- [ ] `cfgreader.py instance id` ohne Default liefert dasselbe wie vorher.
- [ ] `config.skelet` enthält `"standalone":0`.

## Entscheidungen

| Punkt | Entscheidung |
| --- | --- |
| Unit-Abhängigkeit von `restapi-mcp` | Bleibt bei `After=restapi.<instanz>.service`, ohne `Requires=`. Auf einem Entwicklungssystem startet systemd `restapi` deshalb nicht mit. |
| `install.sh` | Legt weiterhin immer alle Units an. |
| Name des Flags | `standalone` |
