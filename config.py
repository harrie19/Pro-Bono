import configparser
import logging

class Configuration:
    """Verwaltet die Konfiguration der Anwendung."""
    def __init__(self, config_file='config.ini'):
        parser = configparser.ConfigParser()
        parser.read(config_file)

        self.log_file = parser.get('Logging', 'LogFile', fallback='app.log')
        self.log_level = logging.INFO

        self.openweathermap_key = parser.get('API', 'openweathermap_key', fallback=None)
        self.policy_url = parser.get('Policy', 'url', fallback=None)
        self.flight_recorder_url = parser.get('FlightRecorder', 'url', fallback=None)
