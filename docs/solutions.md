# Eigene Lösungen (Zusatzmodule)

Eigene Lösungen wie IoTSensorNet oder tuxlog liegen in einem eigenen Repository. Sie werden mit `tools/solution.py` in eine restapi-Instanz importiert.

## Aufbau des Lösungsordners

```
<repo>/restapi/
    solution.json        Pflicht: ID und Name der Lösung (siehe IoTSensorNet/restapi/solution.json)
    database/install.sql Tabellen, Metadaten, Plugin-Registrierung, Views, Menüs
    plugins/             Plugin-Module (nur Dateien, keine Unterordner)
    wwwroot/             Templates und statische Dateien
```

`solution.py` verarbeitet nur `database/install.sql`, `plugins/` und `wwwroot/`. Andere Ordner im Lösungsordner (z. B. `tools/`, `test/`, `docs/`) werden nicht kopiert.

## Import

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

## Regeln für `database/install.sql`

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
- **Plugins registrieren:** in `api_event_handler` mit `solution_id` (siehe „Aufbau“ in [plugins.md](plugins.md)).

## Regeln für `plugins/`

- **Eindeutige Dateinamen:** Alle Lösungen landen im selben Verzeichnis `<restapi>/plugins/`, und eine Datei mit gleichem Namen wird überschrieben. Verwende deshalb ein Präfix der Lösung (`iot_`, `tuxlog_`, ...).
- **Keine Unterordner:** Lege Hilfsmodule als eigene Dateien mit Präfix an, z. B. `iot_common.py`.
- **Umbenennen oder Löschen:** Entfernt oder umbenannt wird eine Datei nur in der Lösung, nicht in der Instanz. Lösche alte Dateien in `<restapi>/plugins/` von Hand und deaktiviere bzw. entferne die zugehörigen Zeilen in `api_event_handler`.
- **Alternative ohne Kopieren:** `plugin.root` in `config.py` liegt ebenfalls im `PYTHONPATH`. Module dort werden ohne Kopieren gefunden.

## Während des Imports

Zwischen dem Löschen und dem Neuanlegen der eigenen Zeilen in `install.sql` fehlen die Event-Handler der Lösung kurz. Plugins, die in diesem Moment laufen sollten, werden übersprungen. Importiere deshalb möglichst in einer ruhigen Zeit, und starte die Dienste direkt danach neu.

## Checkliste

- [ ] `solution.json` vorhanden
- [ ] `install.sql` mehrfach ausführbar: `CREATE TABLE IF NOT EXISTS`, `ADD COLUMN IF NOT EXISTS`, kein `DROP TABLE`/`TRUNCATE` auf Datentabellen
- [ ] Nur Zeilen der eigenen `solution_id` gelöscht und neu angelegt
- [ ] IDs im eigenen Bereich
- [ ] Neue Tabellen in `api_table` mit Rechten in `api_group_permission`, nur so weit wie nötig
- [ ] Plugin-Dateien mit dem Präfix der Lösung, keine Unterordner
- [ ] Plugins erfüllen die Checkliste in [plugins.md](plugins.md)
- [ ] Nach dem Import: `tools/metadata.py` (bei geänderten Tabellen) und `./services.sh restart`
