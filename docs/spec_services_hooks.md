# Spezifikation: Hooks für services.sh

Stand: 2026-11-13

## Ziel und Nicht-Ziele

Nach jeder Aktion (`start`, `stop`, `restart`) führt `tools/services.sh` die Hooks aus `tools/services.d/` aus und zeigt sie in der Ausgabe an. Jeder Hook gehört zu einer Unit und läuft nur, wenn diese Unit in diesem Aufruf erfolgreich gesteuert wurde. Das Verzeichnis ist versioniert, ein Demo-Skript zeigt den Aufbau eines Hooks.

Nicht Teil dieser Änderung:

- Hooks *vor* einer Aktion (pre-Hooks).
- Hooks, die zu keiner Unit gehören.
- Ein Abbruch der Aktion durch einen Hook. Die Units sind schon gesteuert, wenn die Hooks laufen.

## Ablauf

Die Hooks laufen einmal, nachdem alle Units der Aktion gesteuert sind. Es laufen nur die Hooks der Units, bei denen `systemctl <aktion>` erfolgreich war.

1. Argument prüfen, `config.py` lesen, Units bestimmen (wie bisher).
2. Alle Units mit `systemctl <aktion>` steuern und sich merken, welche erfolgreich waren.
3. Für jede Unit in der Reihenfolge der Aktion (bei `stop` rückwärts):
    1. Unit fehlgeschlagen: ihre Hooks werden als übersprungen angezeigt und nicht ausgeführt.
    2. Unit erfolgreich: ihre Hooks für die Aktion aus `tools/services.d/<unit>/` nacheinander ausführen.
4. Exit-Code bilden aus den Fehlern der Units und der Hooks.

Hooks von Units, die in diesem Modus nicht gesteuert werden, laufen nie. Auf einem Entwicklungssystem (`standalone=1`) laufen also die Hooks von `restapi-dev`, aber nicht die von `restapi`, auf einem Produktionssystem umgekehrt.

## Verzeichnis und Namensschema

Hooks liegen in einem Unterverzeichnis pro Unit, `tools/services.d/<unit>/<aktion>-<NN>-<name>.sh`. Das Verzeichnis kommt mit ins Git, außer lokalen Hooks.

| Teil | Werte | Bedeutung |
| --- | --- | --- |
| `<unit>` | `restapi`, `restapi-dev`, `restapi-msg`, `restapi-mcp`, `restapi-timer` | Unit ohne Instanz-ID und ohne `.service`. Das Verzeichnis gilt so für jede Instanz. |
| `<aktion>` | `start`, `stop`, `restart`, `any` | Aktion, nach der der Hook läuft. `any` läuft nach `start` und `restart`, nicht nach `stop`. |
| `<NN>` | `00` bis `99` | Reihenfolge innerhalb der Unit. Erst laufen die Hooks der konkreten Aktion, dann die `any`-Hooks, jeweils nach Dateinamen sortiert. |
| `<name>` | frei, ohne Leerzeichen | Beschreibung, erscheint in der Ausgabe. |

- Ausgeführt werden nur Dateien mit gesetztem Ausführungsrecht. Ein Hook lässt sich mit `chmod -x` abschalten, ohne ihn zu löschen. Git speichert das Ausführungsrecht mit.
- **Lokale Hooks** enden auf `.local.sh`, zum Beispiel `restapi/restart-50-backup.local.sh`. Sie folgen demselben Schema und laufen wie alle anderen, gehen aber nicht ins Git: `.gitignore` bekommt `tools/services.d/**/*.local.sh`. So kann jede Instanz eigene Hooks haben.
- Dateien, die nicht zum Schema passen, und Verzeichnisse ohne passende Unit werden ignoriert, zum Beispiel `README.md`.
- Fehlt das Verzeichnis einer Unit oder enthält es keinen passenden Hook, läuft `services.sh` für diese Unit ohne Meldung wie bisher.

Beispiel für `restart` auf einem Entwicklungssystem, alle Units erfolgreich:

```
tools/services.d/
├── restapi/
│   └── restart-10-reload-apache.sh    läuft nicht (Unit wird nicht gesteuert)
├── restapi-dev/
│   ├── restart-10-cache.sh            1.
│   └── any-90-demo.sh                 2.
└── restapi-mcp/
    └── start-10-notify.sh             läuft nicht (andere Aktion)
```

## Schnittstelle

Ein Hook bekommt die Aktion, die Instanz und die Unit als Argumente und den Rest als Umgebungsvariablen. Er läuft im Repo-Root als Arbeitsverzeichnis, mit dem Benutzer, der `services.sh` aufgerufen hat. Braucht er root-Rechte, ruft er selbst `sudo -n <befehl>` auf. Das Passwort hat `services.sh` dann schon abgefragt. Ist die Merkzeit von `sudo` abgelaufen, schlägt `-n` sofort fehl, statt unter dem Spinner auf ein Passwort zu warten, und der Hook erscheint mit `✘`.

| Name | Art | Beispiel | Inhalt |
| --- | --- | --- | --- |
| `$1` | Argument | `restart` | Ausgeführte Aktion |
| `$2` | Argument | `dev` | Instanz-ID |
| `$3` | Argument | `restapi-dev.dev.service` | Unit, zu der der Hook gehört |
| `SERVICES_ACTION` | Umgebung | `restart` | wie `$1` |
| `SERVICES_INSTANCE_ID` | Umgebung | `dev` | wie `$2` |
| `SERVICES_UNIT` | Umgebung | `restapi-dev.dev.service` | wie `$3` |
| `SERVICES_MODE` | Umgebung | `standalone` | `standalone` oder `uwsgi` |
| `SERVICES_API_UNIT` | Umgebung | `restapi-dev.dev.service` | Gesteuerte API-Unit |
| `SERVICES_UNITS` | Umgebung | `restapi-dev.dev.service restapi-msg.dev.service …` | Alle gesteuerten Units, durch Leerzeichen getrennt |
| `SERVICES_FAILED` | Umgebung | `0` | Anzahl fehlgeschlagener Units |
| `SERVICES_BASEDIR` | Umgebung | `/home/dk9mbs/src/restapi` | Repo-Root |

Stdin ist `/dev/null`. Ein Hook kann also nicht auf eine Eingabe warten und das Skript blockieren.

## Ausgabe und Fehlerverhalten

Jeder Hook bekommt eine eigene Zeile im selben Stil wie die Units, mit `<unit>/<datei>`. Seine Ausgabe erscheint nur, wenn er fehlschlägt, dann um 4 Leerzeichen eingerückt darunter, wie bei den Units.

```
Instance: dev (standalone)
✔ restart restapi-dev.dev.service
✘ restart restapi-msg.dev.service
    Job for restapi-msg.dev.service failed …
✔ restart restapi-mcp.dev.service
✔ restart restapi-timer.dev.service
✔ hook restapi-dev/any-90-demo.sh
✘ hook restapi-mcp/restart-20-check.sh
    restapi-mcp.dev.service does not answer on port 8000
- hook restapi-msg/restart-10-flush.sh (skipped, unit failed)
1 unit(s) failed, 1 hook(s) failed
```

- Während der Hook läuft, dreht sich der Spinner vor `hook <unit>/<datei>` wie bei den Units.
- Die Ausgabe des Hooks (stdout und stderr) wird gesammelt und nur bei einem Exit-Code ungleich 0 angezeigt. Bei Erfolg steht nur seine Zeile da.
- Hooks einer fehlgeschlagenen Unit erscheinen mit `-` und `(skipped, unit failed)`. Sie zählen nicht als zusätzlicher Fehler, die Unit ist schon gezählt.
- Ein Exit-Code ungleich 0 gibt `✘ hook <unit>/<datei>` und zählt als Fehler. Die weiteren Hooks laufen trotzdem.
- Gab es einen Fehler bei einer Unit oder einem Hook, endet `services.sh` mit Exit-Code 1. Die Schlusszeile nennt beides getrennt, zum Beispiel `1 unit(s) failed, 1 hook(s) failed`.

## Betrieb ohne Terminal (Cron)

Ohne Terminal, also zum Beispiel aus einem Cronjob, gibt `services.sh` keine Farben aus und fragt nie nach einem Passwort. Geprüft wird mit `[ -t 1 ]` wie beim Spinner.

| | Mit Terminal | Ohne Terminal |
| --- | --- | --- |
| Spinner | ja | nein (wie bisher) |
| Farben für `✔`, `✘`, `!` | ja | nein, nur die Zeichen |
| sudo-Prüfung als normaler Benutzer | `sudo -v`, fragt nach dem Passwort | `sudo -n -v`, fragt nie |

Schlägt `sudo -n -v` fehl, bricht das Skript vor dem ersten `systemctl` mit Exit-Code 1 und dieser Meldung ab:

```
ERROR: services.sh needs root or passwordless sudo when run without a terminal
```

Empfohlen für Cron ist ein Eintrag als root, zum Beispiel in `/etc/cron.d/restapi`:

```
0 4 * * * root /home/dk9mbs/src/restapi/tools/services.sh restart
```

## Demo-Skript

`tools/services.d/restapi-dev/any-90-demo.sh` läuft nach `start` und `restart`, aber nur auf Entwicklungssystemen, weil nur dort `restapi-dev` gesteuert wird. Es gibt aus, was ein Hook zur Verfügung hat, und ändert nichts am System. Seine Ausgabe ist nur zu sehen, wenn es fehlschlägt, also wenn `restapi-dev` nach `start` oder `restart` nicht läuft. Es wird mit Ausführungsrecht eingecheckt.

```bash
#!/bin/bash

#
# Demo hook for tools/services.sh
# runs after start and restart of restapi-dev,
# i.e. only on development systems (instance.standalone=1)
#
# path: services.d/<unit>/<action>-<NN>-<name>.sh
# action: start, stop, restart or any (any = start and restart)
# local hooks not in git: <action>-<NN>-<name>.local.sh
# disable a hook with: chmod -x <file>
# commands that need root: sudo -n <command> (never prompts, fails instead)
# output is only shown if the hook fails (exit code != 0)
#

echo "demo hook: action=$1 instance=$2 unit=$3 failed=$SERVICES_FAILED"

if systemctl is-active --quiet "$SERVICES_UNIT";
then
    echo "$SERVICES_UNIT is active"
else
    echo "$SERVICES_UNIT is not active"
    exit 1
fi
```

Das Skript zeigt zwei Dinge: Argumente und Umgebungsvariablen lesen und über den Exit-Code einen Fehler melden.

## Abnahmekriterien

- [ ] Nach `restart` laufen für jede erfolgreich gesteuerte Unit genau ihre ausführbaren Hooks `restart-*` und danach `any-*`, in der Reihenfolge der Units. Nach `stop` laufen nur `stop-*`, keine `any-*`.
- [ ] Mit `standalone=1` laufen die Hooks unter `restapi-dev/`, nie die unter `restapi/`. Mit `standalone=0` umgekehrt.
- [ ] Hooks einer fehlgeschlagenen Unit laufen nicht und erscheinen als `(skipped, unit failed)`.
- [ ] Hooks für andere Aktionen, Dateien ohne Ausführungsrecht und Dateien außerhalb des Schemas laufen nicht.
- [ ] Jeder Hook erscheint mit eigener Zeile `hook <unit>/<datei>`. Seine Ausgabe erscheint nur bei einem Exit-Code ungleich 0, eingerückt darunter.
- [ ] Ein Hook mit Exit-Code 1 ergibt `✘`, die folgenden Hooks laufen weiter, `services.sh` endet mit Exit-Code 1.
- [ ] Ein Hook `*.local.sh` läuft wie jeder andere, und `git status` zeigt ihn nicht an.
- [ ] Ohne `tools/services.d/` oder ohne passende Hooks ist die Ausgabe dieselbe wie vorher.
- [ ] `tools/services.d/restapi-dev/any-90-demo.sh` ist mit Ausführungsrecht (Modus 100755) im Git.
- [ ] Ohne Terminal (`services.sh restart > log`) enthält die Ausgabe keine ANSI-Escape-Sequenzen.
- [ ] Ohne Terminal und ohne passwortloses sudo bricht das Skript mit der Meldung oben und Exit-Code 1 ab, ohne eine Unit anzufassen.
- [ ] Als root läuft das Skript ohne Terminal vollständig durch.

## Entscheidungen

| Punkt | Entscheidung |
| --- | --- |
| Demo aktiv oder inaktiv | Die Demo liegt unter `restapi-dev/` und läuft damit nur auf Entwicklungssystemen. |
| Instanz-spezifische Hooks | Ja, als lokale Hooks `*.local.sh`, die per `.gitignore` nicht ins Git gehen. |
| Ausgabe bei Erfolg | Nur bei Fehlern, wie bei den Units. |
| `any`-Hooks bei stop | `any` läuft nur nach `start` und `restart`. Nach `stop` laufen nur `stop-*`-Hooks. |
