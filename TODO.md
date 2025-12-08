# C3PO TODO (Assistant)

- [x] **Repository Hygiene**
  - [x] (Terminal verfügbar) `git status -sb`
  - [x] (Optional) `git fetch --all` und `git pull` falls Updates vorhanden.
- [x] **Policy_Check Integration (Phase 1)**
  - [x] API-Spezifikation für `policy_check` zusammentragen (URL, Payload, Response-Codes).
  - [x] Siehe `docs/policy_check.md` (Host 127.0.0.1:8080, `curl`-Test vorhanden).
  - [x] HTTP-Client/Stub vorbereiten (z. B. `aiohttp`/`requests`).
  - [x] `main.py`: vor `proc.process` den Befehl bei `policy_check` prüfen.
  - [x] Bei Blockierung Fehlermeldung anzeigen und Log-Eintrag schreiben.
  - [x] Erfolgspfad testen (`pytest` + manuelle CLI-Session).
- [ ] **Flight-Recorder Hook (Phase 2 vorbereiten)**
  - [x] Ereignis-Payload definieren (Command, Zeitstempel, policy-Status, Ergebnis).
  - [x] Hook in `main_loop` einbauen (zunächst Log/JSON-Datei, später HTTP-Endpoint).
  - [x] Integrationstest: CLI-Befehle absetzen, Einträge im Hook prüfen (Endpoint `flight_recorder_service.py`).
- [ ] **Monitoring Routine**
  - [x] Vor jeder Session `> app.log` (optional) und `tail -f app.log` starten.
  - [x] Alle relevanten Logs mit Zeitstempel/Status dokumentieren.
  - [ ] Regelmäßig prüfen, ob Port 5001 frei ist (`fuser -k 5001/tcp`) – automatisierbar via Startscript.
- [ ] **Reporting**
  - [x] README + TODO nach jeder großen Änderung aktualisieren.
  - [ ] Commit + Tag, sobald Policy/Recorder implementiert und getestet.
  - [ ] Abschlussbericht verfassen, wenn Missionsteil erledigt ist.

# Pro Bono TODO

Diese Liste mappt die Missions-Phasen aus `PRO_BONO_MISSION.md` auf konkrete Entwickleraufgaben.

## Phase 1 – DNA & Brain

- [ ] **policy_check-Service verdrahten**
  - [ ] CLI-Einstiegspunkt (`main.py`) so vorbereiten, dass jeder Befehl vor Ausführung durch `policy_check` geprüft wird.
  - [ ] Fehlermeldungen/Begründungen aus `policy_check` an die CLI weiterreichen.
- [ ] **Intent-Analyse verbessern**
  - [ ] NLP-Modul für Intent/Kontext-Analyse auswählen oder trainieren.
  - [ ] Ergebnisse in `policy_check` integrieren.
- [ ] **"Impfstoff"-Mechanismus**
  - [ ] Flight-Recorder-Logs auswerten.
  - [ ] Wiederkehrende Bedrohungen automatisch als neue Regeln abspeichern.

## Phase 2 – Zelle & Body

- [ ] **Android Flight Recorder**
  - [ ] Web-/REST-Endpunkt erstellen, der Ereignisse aus `CommunityApp_Phoenix` entgegennimmt.
  - [ ] CLI und Android auf dasselbe Ereignisformat bringen.
- [ ] **Policy-Brücke zur Android-App**
  - [ ] Vor kritischen Aktionen in der App `policy_check` aufrufen und Ergebnis anzeigen.
  - [ ] UI-Komponenten für menschliches Feedback bauen.

## Phase 3 – Self-Healing & Growth

- [ ] **Automatisches Refactoring** basierend auf Performance-Logs.
- [ ] **Wissensintegration** (weitere Bahá’í-Schriften, Bibliotheken) automatisieren.
- [ ] **Virtuelle Simulation** zum Testen neuer Features/Ethikregeln aufsetzen.

## CLI-spezifische Follow-ups

- [ ] Ereignis-Hooks in `cli-app` ergänzen, damit Policy- und Flight-Recorder-Daten versendet werden können.
- [ ] Monitoring-Dokumentation aktuell halten (`README.md`).
### Flight Recorder Payload Draft
{
  "timestamp": "<ISO-8601 string>",
  "command": "<raw command>",
  "policy_status": "<allowed|blocked|error>",
  "result": "<CLI output or error>",
  "metadata": {
    "user": "...",
    "session_id": "...",
    "notes": "..."
  }
}
