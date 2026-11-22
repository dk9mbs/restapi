# Entwickler-Doku in Claude nutzen

Der MCP-Server der restapi (`mcpservice.py`) stellt die Dokumente aus `docs/` bereit, und zwar auf zwei Wegen:

- **Tool `get_doc`:** Claude schlägt selbst nach. Ohne Parameter bekommt es den Index, mit `name` ein Dokument.
- **Resources `docs://<name>`:** Du hängst ein Dokument gezielt an deine Nachricht an.

Es gibt nur Dokumente, die in [index.md](index.md) verlinkt sind.

## Einrichten

### Claude Code

Remote über Apache (siehe `examples/apache2/mcp.conf`):

```bash
claude mcp add --transport http restapi https://<host>/mcp \
  --header "Authorization: Bearer <token>"
```

Oder lokal über stdio:

```bash
claude mcp add restapi \
  -e DK9MBS_API_BASE=https://<host>/api -e DK9MBS_API_KEY=<apikey> \
  -- /pfad/zur/restapi/venv/mcp/bin/python /pfad/zur/restapi/mcpservice.py
```

Mit `/mcp` in Claude Code siehst du, ob der Server verbunden ist und welche Tools und Resources er anbietet.

### claude.ai / Claude Desktop

Unter **Einstellungen → Connectors** den MCP-Server als eigenen Connector hinzufügen, mit der URL `https://<host>/mcp`. Danach steht er im Chat über das Menü **+** bzw. das Tool-Symbol zur Verfügung.

## Claude selbst nachschlagen lassen (Tool)

Stell einfach deine Frage. Claude ruft `get_doc` auf, liest den Index und lädt das passende Dokument nach. Damit das sicher passiert, hilft ein Hinweis wie „schau in die restapi-Doku“:

```
Schau in die restapi-Doku: Wie lese ich mit FetchXML alle Sensoren,
die in den letzten 2 Stunden Daten geliefert haben?
```

```
Lies die Plugin-Richtlinie aus der restapi-Doku und schreib mir ein
before-insert-Plugin für iot_sensor_data, das Werte außerhalb von
-50 bis 100 °C ablehnt.
```

```
Prüf dieses Plugin gegen die Checkliste in plugins.md aus der restapi-Doku:
<Code einfügen>
```

```
Welche Dokumente gibt es in der restapi-Doku?
```

## Dokument gezielt anhängen (Resource)

### Claude Code

Tippe `@` und wähle das Dokument aus der Liste, oder schreib es direkt:

```
@restapi:docs://fetchxml.md Bau mir eine FetchXML, die pro Gerät die
Anzahl der Messwerte von heute zählt.
```

```
@restapi:docs://plugins.md @restapi:docs://solutions.md
Leg mir das Gerüst für eine neue Lösung "garden" mit einem Timer-Plugin an.
```

`restapi` ist der Name aus `claude mcp add`. Hast du einen anderen Namen vergeben, steht hier dieser.

### claude.ai / Claude Desktop

Im Chat über **+** den restapi-Connector wählen und dort das Dokument, z. B. `plugins.md`. Es erscheint wie eine angehängte Datei über dem Eingabefeld. Danach die Frage stellen:

```
Erklär mir anhand des angehängten Dokuments, wann ich run_as_system
verwenden darf.
```

Ob Resources angeboten werden, hängt vom Client ab. Wenn das Menü keine Dokumente zeigt, nimm den Weg über das Tool.

## Tipps

- **Ein konkretes Dokument nennen:** Das spart den Umweg über den Index, z. B. „lies `fetchxml.md` aus der restapi-Doku“.
- **Mehrere Dokumente:** Für eine neue Lösung brauchst du meist `plugins.md`, `solutions.md` und `fetchxml.md` zusammen.
- **Neue Dokumente:** Ein neues Dokument muss in `index.md` verlinkt sein. Danach `git pull` auf dem Server. Das Tool sieht es sofort, die Liste der Resources nach `systemctl reload restapi-mcp.<instance>.service`.
