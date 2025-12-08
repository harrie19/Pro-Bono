import pytest
import asyncio
from unittest.mock import patch, MagicMock

from command_processor import CommandProcessor
from config import Configuration

@pytest.fixture
def config():
    """Stellt eine Mock-Konfiguration für Tests bereit."""
    # Wir verwenden eine einfache MagicMock anstelle des Lesens einer echten Datei
    mock_config = MagicMock(spec=Configuration)
    mock_config.openweathermap_key = "test_api_key"
    return mock_config

@pytest.fixture
def processor(config):
    """Stellt eine CommandProcessor-Instanz mit der echten Command-Liste bereit."""
    return CommandProcessor(config)

@pytest.mark.asyncio
async def test_process_hilfe_command(processor):
    """Testet, ob der Default-Hilfe-Befehl korrekt funktioniert."""
    result = await processor.process("Hilfe")
    assert result['status'] == 'success'
    assert "Verfügbare Befehle:" in result['result']
    # Korrigierte Beschreibung, die der echten Implementierung entspricht
    assert "Wetter: Ruft das Wetter für eine Stadt ab. Format: Wetter:<stadt>" in result['result']

    result_lower = await processor.process("hilfe")
    assert result_lower['status'] == 'success'
    assert "Verfügbare Befehle:" in result_lower['result']

@pytest.mark.asyncio
async def test_process_wetter_command_success(processor):
    """Testet die erfolgreiche Ausführung des Wetter-Befehls mit gemocktem HTTP-Aufruf."""

    class DummyResponse:
        def __init__(self, status, payload):
            self.status = status
            self._payload = payload

        async def json(self):
            return self._payload

    class DummyResponseCtx:
        def __init__(self, response):
            self._response = response

        async def __aenter__(self):
            return self._response

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class DummySession:
        def __init__(self, response):
            self._response = response

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def get(self, url):
            return DummyResponseCtx(self._response)

    dummy_payload = {
        "weather": [{"description": "klarer Himmel"}],
        "main": {"temp": 25.0}
    }

    with patch('commands.aiohttp.ClientSession', return_value=DummySession(DummyResponse(200, dummy_payload))):
        result = await processor.process("Wetter:Teststadt")

    assert result['status'] == 'success'
    assert "Wetter in Teststadt: klarer Himmel, Temperatur: 25.0°C" == result['result']

@pytest.mark.asyncio
async def test_process_wetter_command_no_city(processor):
    """Testet den Wetter-Befehl ohne Angabe einer Stadt."""
    result = await processor.process("Wetter:")
    assert result['status'] == 'error'
    # Korrigierte Fehlermeldung
    assert result['result'] == "Fehler: Stadt erforderlich."

@pytest.mark.asyncio
async def test_process_unknown_command(processor):
    """Testet die Eingabe eines unbekannten Befehls."""
    result = await processor.process("Unbekannt:Test")
    assert result['status'] == 'error'
    assert result['result'] == "Befehl 'Unbekannt' nicht gefunden."

@pytest.mark.asyncio
async def test_process_empty_input(processor):
    """Testet eine leere Eingabe."""
    result = await processor.process("")
    assert result['status'] == 'error'
    assert result['result'] == "Kein Befehl eingegeben."

@pytest.mark.asyncio
async def test_wetter_command_no_api_key():
    """Testet den Fall, dass kein API-Schlüssel konfiguriert ist."""
    mock_config = MagicMock(spec=Configuration)
    mock_config.openweathermap_key = None

    processor_no_key = CommandProcessor(mock_config)
    result = await processor_no_key.process("Wetter:Berlin")
    assert result['status'] == 'error'
    assert result['result'] == "Fehler: OpenWeatherMap API-Schlüssel nicht in config.ini konfiguriert."

@pytest.mark.asyncio
async def test_process_time_command(processor):
    """Stellt sicher, dass der Zeit-Befehl einen Erfolg liefert."""
    result = await processor.process("Zeit")
    assert result['status'] == 'success'
    assert result['result'].startswith("Aktuelle Zeit:")
