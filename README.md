# Python CLI App

Eine interaktive, erweiterbare Kommandozeilenanwendung, die als Demonstration für eine modulare und asynchrone Architektur dient.

## Installation

1.  **Klonen Sie das Repository** (falls zutreffend) und wechseln Sie in das Verzeichnis.

2.  **Installieren Sie das Paket:**
    *   Für die normale Benutzung:
        ```bash
        pip install .
        ```
    *   Für die Entwicklung (Änderungen werden sofort wirksam):
        ```bash
        pip install -e .
        ```

## Benutzung

Nach der Installation können Sie die Anwendung von überall im Terminal ausführen:

```bash
cli-app
```

Innerhalb der Anwendung können Sie Befehle eingeben. Mit `Hilfe` erhalten Sie eine Liste aller verfügbaren Befehle.

### Unterstützte Befehle (Auszug)

| Befehl        | Format                            | Beschreibung |
|---------------|-----------------------------------|--------------|
| `Hilfe`       | `Hilfe`                           | Listet alle Befehle auf. |
| `Analyse`     | `Analyse:<text>`                  | Zählt Wörter und Zeichen im Text. |
| `Lesen`       | `Lesen:<dateiname>`               | Liest den Inhalt einer Datei. |
| `Speichern`   | `Speichern:<dateiname>:<inhalt>`  | Schreibt Inhalt in eine Datei. |
| `Löschen`     | `Löschen:<dateiname>`             | Entfernt eine Datei. |
| `Netzwerk`    | `Netzwerk:<url>`                  | Führt eine HTTP-GET-Anfrage aus. |
| `Rechner`     | `Rechner:<ausdruck>`              | Bewertet einfache mathematische Ausdrücke. |
| `Wetter`      | `Wetter:<stadt>`                  | Ruft Wetterdaten über den OpenWeatherMap-API-Schlüssel aus `config.ini` ab. |
| `Zeit`        | `Zeit`                            | Gibt das aktuelle Datum und die Uhrzeit aus. |
| `exit`        | `exit`                            | Beendet die Anwendung. |

### Beispiele

```bash
> Hilfe
> Zeit
> Analyse:Dies ist ein Test
> Wetter:Berlin
> Speichern:notes.txt:Hallo Welt
> Lesen:notes.txt
> Löschen:notes.txt
```

> **Hinweis:** Der Wetterbefehl benötigt einen gültigen API-Schlüssel im Abschnitt `[API]` der `config.ini`:
> ```ini
> [API]
> openweathermap_key = IHR_API_SCHLUESSEL
> ```

## Monitoring & Policy-Integration

- Lass während einer CLI-Sitzung ein zweites Terminal mitlaufen:

```bash
cd /home/marek/app2app/Pro-Bono
tail -f app.log
```

  So siehst du für jeden Befehl sofort `Status: success` oder Fehler. Vor einer neuen Session kannst du das Log schnell leeren:

```bash
cd /home/marek/app2app/Pro-Bono
> app.log
```

- Sobald die `policy_check`-Schnittstelle bereitsteht, sollten Befehle in `main.py` vor Ausführung dort validiert werden. Erfolgreiche Prüfungen/Blocker müssen im Log landen, damit der „Flight Recorder“ ein vollständiges Protokoll besitzt.
- Androids „Flight Recorder“ (siehe `TODO.md`, Phase 2) kann auf das gleiche Eventformat aufsetzen – die CLI dient als Referenz für Payload-Struktur und Logging-Konventionen.

### Policy-Service starten

```bash
cd /home/marek/app2app/Pro-Bono
FLASK_ENV=production python policy_service.py
```

Der Service lauscht auf `http://127.0.0.1:8080`. Teste ihn mit:

```bash
curl -X POST http://127.0.0.1:8080/policy_check \
  -H "Content-Type: application/json" \
  -d '{"command": "read file.txt", "context": {"user_role": "admin"}}'
```

Während `cli-app` läuft, schreibt das System jede Policy-Entscheidung nach `flight_recorder.log`.

### Flight-Recorder starten

```bash
cd /home/marek/app2app/Pro-Bono
FLASK_ENV=production python flight_recorder_service.py
```

Teste die Schnittstelle mit:

```bash
curl -X POST http://127.0.0.1:8090/flight_record \
  -H "Content-Type: application/json" \
  -d '{"command": "Zeit", "policy_status": "approved", "result": "Demo"}'
```

Der CLI-Recorder sendet jeden Eintrag automatisch an diesen Service.
