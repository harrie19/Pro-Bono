import inspect
import commands
import logging
from typing import Dict, Any

class CommandProcessor:
    def __init__(self, config: Any):
        self.config = config
        self.commands = self._discover_commands()

        # FALLBACK: Wenn keine Hilfe vorhanden ist, stelle eine Default-Hilfe sicher
        if 'hilfe' not in self.commands and 'Hilfe' not in self.commands:
            class _DefaultHelp:
                def __init__(self, commands_dict: Dict[str, Any]):
                    self._commands = commands_dict
                    self.description = "Zeigt verfügbare Befehle an."

                def execute(self, value: str = "") -> Dict[str, str]:
                    lines = ["Verfügbare Befehle:"]
                    seen = set()
                    for k in sorted(self._commands.keys(), key=lambda s: s.lower()):
                        kl = k.lower()
                        if kl in seen or kl == 'hilfe':
                            continue
                        seen.add(kl)
                        cmd = self._commands[k]
                        desc = getattr(cmd, 'description', None) or (cmd.__doc__ or '').strip()
                        display_name = kl.capitalize()
                        if desc:
                            desc_line = desc.splitlines()[0]
                            lines.append(f"- {display_name}: {desc_line}")
                        else:
                            lines.append(f"- {display_name}")
                    return {"status": "success", "result": "\n".join(lines)}

            help_inst = _DefaultHelp(self.commands)
            self.commands['hilfe'] = help_inst
            self.commands['Hilfe'] = help_inst

        # Debug: liste geladene Befehle auf
        try:
            logging.info(f"CommandProcessor: geladene Befehle: {sorted(self.commands.keys())}")
        except Exception:
            pass

    def _discover_commands(self) -> Dict[str, Any]:
        """Findet und instanziiert alle Command-Klassen im 'commands'-Modul.

        - Überspringt explizit definierte Basisklassen wie BaseCommand.
        - Versucht, Konstruktor-Parameter (z. B. config, commands) zu erkennen und zu übergeben.
        - Überspringt Klassen, die bei der Instanziierung Fehler werfen.
        - Speichert Command-Namen in lowercase und Capitalized Form für robuste Lookup.
        """
        discovered_commands: Dict[str, Any] = {}

        base_cls = getattr(commands, 'BaseCommand', None)

        for name, obj in inspect.getmembers(commands, inspect.isclass):
            # Nur Klassen mit dem 'Command'-Suffix betrachten
            if not name.endswith('Command'):
                continue

            # Überspringe die Basisklasse selbst
            if base_cls is not None and obj is base_cls:
                continue

            # Skip HilfeCommand here; wird gesondert initialisiert
            if name == 'HilfeCommand':
                continue

            # Prüfe, ob es sinnvoll ist, die Klasse zu behandeln
            try:
                if base_cls is not None:
                    if not issubclass(obj, base_cls):
                        # Wenn es keine Unterklasse der BaseCommand ist, dann nur aufnehmen,
                        # falls eine execute()-Methode vorhanden ist
                        if not hasattr(obj, 'execute'):
                            continue
                else:
                    # Kein BaseCommand definiert -> akzeptiere Klassen mit execute
                    if not hasattr(obj, 'execute'):
                        continue

                # Erzeuge Instanz und übergebe gegebenenfalls 'config'
                ctor_sig = inspect.signature(obj.__init__)
                kwargs = {}
                if 'config' in ctor_sig.parameters:
                    kwargs['config'] = self.config
                # Manche Commands erwarten 'commands' oder andere Parameter — wir übergeben nur 'config' hier

                instance = obj(**kwargs)
                command_name = name.replace('Command', '')
                # Speichere beide Varianten: lowercase (für parsing) und Capitalized (für ältere callers)
                discovered_commands[command_name.lower()] = instance
                discovered_commands[command_name.capitalize()] = instance
            except Exception:
                # Wenn die Klasse nicht instanziiert werden kann, überspringe sie (robustheit)
                continue

        # Initialisiere HilfeCommand separat mit der Liste anderer Befehle und optional config
        if hasattr(commands, 'HilfeCommand'):
            HilfeCls = getattr(commands, 'HilfeCommand')
            try:
                help_ctor_sig = inspect.signature(HilfeCls.__init__)
                help_kwargs = {}
                # Versuche unterschiedliche mögliche Parameter
                if 'commands' in help_ctor_sig.parameters:
                    help_kwargs['commands'] = discovered_commands
                if 'config' in help_ctor_sig.parameters:
                    help_kwargs['config'] = self.config

                # Wenn help_kwargs noch leer ist, übergebe discovered_commands als positional
                if help_kwargs:
                    help_inst = HilfeCls(**help_kwargs)
                else:
                    help_inst = HilfeCls(discovered_commands)

                discovered_commands['hilfe'] = help_inst
                discovered_commands['Hilfe'] = help_inst
            except Exception:
                # Ignoriere Fehler beim Erstellen der Hilfe-Instanz
                pass

        # FALLBACK: Wenn weiterhin kein 'Hilfe' vorhanden ist, erstelle eine Default-Hilfe
        if 'hilfe' not in discovered_commands and 'Hilfe' not in discovered_commands:
            class _DefaultHelp:
                """Ein einfacher Help-Command, falls keine Hilfe-Klasse gefunden/instanziiert werden konnte."""
                def __init__(self, commands_dict: Dict[str, Any]):
                    self._commands = commands_dict
                    self.description = "Zeigt verfügbare Befehle an."

                def execute(self, value: str = "") -> Dict[str, str]:
                    lines = ["Verfügbare Befehle:"]
                    # Wir zeigen nur die lowercase Schlüssel (Menschenfreundlich)
                    seen = set()
                    for k in sorted(self._commands.keys(), key=lambda s: s.lower()):
                        kl = k.lower()
                        if kl in seen or kl == 'hilfe':
                            continue
                        seen.add(kl)
                        cmd = self._commands[k]
                        desc = getattr(cmd, 'description', None) or (cmd.__doc__ or '').strip()
                        display_name = kl.capitalize()
                        if desc:
                            # Nur die erste Zeile der Beschreibung
                            desc_line = desc.splitlines()[0]
                            lines.append(f"- {display_name}: {desc_line}")
                        else:
                            lines.append(f"- {display_name}")
                    return {"status": "success", "result": "\n".join(lines)}

            help_inst = _DefaultHelp(discovered_commands)
            discovered_commands['hilfe'] = help_inst
            discovered_commands['Hilfe'] = help_inst

        return discovered_commands

    def _find_command_case_insensitive(self, name: str):
        """Hilfsfunktion: finde einen command instance per case-insensitive key."""
        if not name:
            return None
        # first direct lookup
        inst = self.commands.get(name)
        if inst:
            return inst
        lower = name.lower()
        inst = self.commands.get(lower)
        if inst:
            return inst
        # fallback: iterate keys
        for k, v in self.commands.items():
            if k.lower() == lower:
                return v
        return None

    async def process(self, raw_command: str) -> Dict[str, str]:
        """Verarbeitet einen rohen Eingabestring im Format 'Befehl:Wert'.

        Gibt ein Dict mit Schlüsseln 'status' und 'result' zurück.
        """
        if not raw_command or not raw_command.strip():
            return {"status": "error", "result": "Kein Befehl eingegeben."}

        parts = raw_command.strip().split(':', 1)
        command_name = parts[0].strip()
        value = parts[1] if len(parts) > 1 else ""

        command_instance = self._find_command_case_insensitive(command_name)

        if command_instance:
            try:
                result = command_instance.execute(value)
                if inspect.isawaitable(result):
                    return await result
                else:
                    return result
            except Exception as e:
                return {"status": "error", "result": f"Fehler beim Ausführen des Befehls: {e}"}
        else:
            return {"status": "error", "result": f"Befehl '{parts[0]}' nicht gefunden."}

    # Rückwärtskompatible Methode (frühere main-Versionen riefen ggf. execute auf)
    async def execute(self, command_name: str, value: str) -> Dict[str, str]:
        instance = self._find_command_case_insensitive(command_name.strip())
        if instance:
            try:
                res = instance.execute(value)
                if inspect.isawaitable(res):
                    return await res
                else:
                    return res
            except Exception as e:
                return {"status": "error", "result": f"Fehler beim Ausführen des Befehls: {e}"}
        else:
            return {"status": "error", "result": f"Befehl '{command_name}' nicht gefunden."}
