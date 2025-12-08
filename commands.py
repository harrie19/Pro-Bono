import abc
import os
import requests
import aiohttp
from datetime import datetime
from typing import Dict, List, Type, Optional
from config import Configuration

class BaseCommand(abc.ABC):
    """Abstrakte Basisklasse für alle Befehle."""
    description: str = "Keine Beschreibung verfügbar."

    def __init__(self, config: Optional[Configuration] = None):
        self._config = config

    @abc.abstractmethod
    async def execute(self, value: str) -> Dict[str, str]:
        """Führt den Befehl aus."""
        pass

class HilfeCommand(BaseCommand):
    """Ein Befehl zur Anzeige der Hilfe."""
    description = "Zeigt diese Hilfe an. Format: Hilfe"

    def __init__(self, all_commands: Dict[str, Type['BaseCommand']], config: Optional[Configuration] = None):
        super().__init__(config)
        self.all_commands = all_commands

    async def execute(self, value: str) -> Dict[str, str]:
        output = ["Verfügbare Befehle:"]
        for name, cmd_class in sorted(self.all_commands.items()):
            output.append(f"- {name}: {cmd_class.description}")
        output.append("- exit: Beendet die Anwendung.")
        return {"status": "success", "result": "\n".join(output)}

class SpeichernCommand(BaseCommand):
    """Ein Befehl zum Speichern von Text in einer Datei."""
    description = "Speichert Text in einer Datei. Format: Speichern:<dateiname>:<inhalt>"

    async def execute(self, value: str) -> Dict[str, str]:
        parts = value.split(':', 1)
        if len(parts) < 2:
            return {"status": "error", "result": "Fehler: Dateiname und Inhalt erforderlich."}
        filename, content = parts
        try:
            with open(filename, 'w') as f:
                f.write(content)
            return {"status": "success", "result": f"Datei '{filename}' erfolgreich gespeichert."}
        except IOError as e:
            return {"status": "error", "result": f"Fehler beim Speichern der Datei: {e}"}

class LesenCommand(BaseCommand):
    """Ein Befehl zum Lesen einer Datei."""
    description = "Liest eine Datei. Format: Lesen:<dateiname>"

    async def execute(self, value: str) -> Dict[str, str]:
        if not value:
            return {"status": "error", "result": "Fehler: Dateiname erforderlich."}
        try:
            with open(value, 'r') as f:
                content = f.read()
            return {"status": "success", "result": content}
        except FileNotFoundError:
            return {"status": "error", "result": "Fehler: Datei nicht gefunden."}
        except IOError as e:
            return {"status": "error", "result": f"Fehler beim Lesen der Datei: {e}"}

class LöschenCommand(BaseCommand):
    """Ein Befehl zum Löschen einer Datei."""
    description = "Löscht eine Datei. Format: Löschen:<dateiname>"

    async def execute(self, value: str) -> Dict[str, str]:
        if not value:
            return {"status": "error", "result": "Fehler: Dateiname erforderlich."}
        try:
            os.remove(value)
            return {"status": "success", "result": f"Datei '{value}' erfolgreich gelöscht."}
        except FileNotFoundError:
            return {"status": "error", "result": "Fehler: Datei nicht gefunden."}
        except OSError as e:
            return {"status": "error", "result": f"Fehler beim Löschen der Datei: {e}"}

class AnalyseCommand(BaseCommand):
    """Ein Befehl zur Analyse eines Textes."""
    description = "Analysiert einen Text. Format: Analyse:<text>"

    async def execute(self, value: str) -> Dict[str, str]:
        if not value:
            return {"status": "error", "result": "Fehler: Kein Text zur Analyse angegeben."}
        word_count = len(value.split())
        char_count = len(value)
        return {"status": "success", "result": f"Analyse: {word_count} Wörter, {char_count} Zeichen."}

class NetzwerkCommand(BaseCommand):
    """Ein Befehl zur Simulation einer Netzwerkanfrage."""
    description = "Simuliert eine Netzwerkanfrage. Format: Netzwerk:<url>"

    async def execute(self, value: str) -> Dict[str, str]:
        if not value:
            return {"status": "error", "result": "Fehler: URL erforderlich."}
        try:
            response = requests.get(value, timeout=5)
            return {"status": "success", "result": f"Antwort von {value}: Status {response.status_code}"}
        except requests.RequestException as e:
            return {"status": "error", "result": f"Netzwerkfehler: {e}"}

class RechnerCommand(BaseCommand):
    """Ein Befehl zur Auswertung eines einfachen mathematischen Ausdrucks."""
    description = "Wertet einen mathematischen Ausdruck aus. Format: Rechner:<ausdruck>"

    async def execute(self, value: str) -> Dict[str, str]:
        if not value:
            return {"status": "error", "result": "Fehler: Kein Ausdruck angegeben."}
        try:
            result = eval(value, {"__builtins__": {}}, {})
            return {"status": "success", "result": f"Ergebnis: {result}"}
        except Exception as e:
            return {"status": "error", "result": f"Fehler bei der Auswertung: {e}"}

class WetterCommand(BaseCommand):
    """Ruft das aktuelle Wetter für eine Stadt ab."""
    description = "Ruft das Wetter für eine Stadt ab. Format: Wetter:<stadt>"

    async def execute(self, value: str) -> Dict[str, str]:
        if not value:
            return {"status": "error", "result": "Fehler: Stadt erforderlich."}
        
        if not self._config or not self._config.openweathermap_key or self._config.openweathermap_key == 'IHR_API_SCHLUESSEL_HIER':
            return {"status": "error", "result": "Fehler: OpenWeatherMap API-Schlüssel nicht in config.ini konfiguriert."}

        city = value.strip()
        api_key = self._config.openweathermap_key
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=de"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        weather = data['weather'][0]['description']
                        temp = data['main']['temp']
                        return {"status": "success", "result": f"Wetter in {city.capitalize()}: {weather}, Temperatur: {temp}°C"}
                    else:
                        data = await response.json()
                        return {"status": "error", "result": f"Fehler beim Abrufen der Wetterdaten: {data.get('message', 'Unbekannter Fehler')}"}
        except aiohttp.ClientError as e:
            return {"status": "error", "result": f"Netzwerkfehler: {e}"}

class ZeitCommand(BaseCommand):
    """Gibt die aktuelle Datum-/Uhrzeitinformation zurück."""
    description = "Zeigt die aktuelle Zeit an. Format: Zeit"

    async def execute(self, value: str) -> Dict[str, str]:
        now = datetime.now()
        formatted = now.strftime("%d.%m.%Y %H:%M:%S")
        return {"status": "success", "result": f"Aktuelle Zeit: {formatted}"}
