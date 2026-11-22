# Dokumentation

Übersicht über alle Dokumente in `docs/`.

## Entwicklung

| Dokument | Inhalt |
|---|---|
| [fetchxml.md](fetchxml.md) | Datenzugriff mit FetchXML: Endpunkte, Aufbau, Lesen, Filter, Anlegen, Ändern, Löschen, Verwendung in Python, Rechte und Fehler |
| [plugins.md](plugins.md) | Plugins schreiben: Aufbau und Registrierung, Ereignisse und `params`, Datenzugriff, Rechte, Eingaben, Zugangsdaten, Fehler, Laufzeit, Threads, eigene Endpunkte, Checkliste |
| [solutions.md](solutions.md) | Eigene Lösungen (Zusatzmodule) mit `tools/solution.py` importieren: Aufbau des Lösungsordners, Regeln für `install.sql` und `plugins/`, Checkliste |
| [mcp-docs.md](mcp-docs.md) | Diese Doku in Claude nutzen: MCP-Server einrichten, Tool `get_doc`, Resources `docs://` anhängen, Beispiel-Prompts |

## Betrieb

| Dokument | Inhalt |
|---|---|
| [uwsgi-threads.md](uwsgi-threads.md) | uWSGI mit Threads, `lazy-apps`, `harakiri` und `post-buffering`: Konfiguration über den Abschnitt `uwsgi` in `config.py`, Tests, Deployment und Rollback |

## Änderungen

Zusammenfassungen einzelner Änderungen mit Ausgangslage, Tests und Deployment.

| Dokument | Inhalt |
|---|---|
| [db-connection-reuse.md](db-connection-reuse.md) | Eine DB-Verbindung pro Request statt 3 bis 5 (20.11.2026) |
| [uwsgi-threads.md](uwsgi-threads.md) | Umstellung von uWSGI auf Threads und `lazy-apps` (20.11.2026) |
