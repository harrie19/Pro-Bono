import asyncio
import logging
import json
import os
import sys
from threading import Thread
from typing import Dict, Any
from datetime import datetime

import aiohttp
from flask import Flask, jsonify, request
from command_processor import CommandProcessor
from config import Configuration

# Logging-Konfiguration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Flask-App für das Web-Interface
app = Flask(__name__)

# Globale Variable für den Prozessor, damit der Web-Endpunkt darauf zugreifen kann
processor: CommandProcessor

@app.route('/command', methods=['POST'])
async def handle_command():
    """Nimmt Befehle über einen Web-Endpunkt entgegen."""
    data = request.json
    if not data or 'command' not in data:
        return jsonify({"status": "error", "result": "Kein Befehl angegeben."}), 400
    
    raw_command = data['command']
    result = await processor.process(raw_command)
    return jsonify(result)

def run_web_interface():
    """Startet das Flask-Web-Interface in einem separaten Thread."""
    try:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        app.run(port=5001, host='127.0.0.1')
    except OSError as e:
        logging.error(f"Fehler beim Starten des Web-Interface: {e}")

async def main_loop(proc: CommandProcessor):
    """Hauptschleife für die interaktive CLI."""
    print("Willkommen zur interaktiven CLI-Anwendung.")
    print("Geben Sie 'Hilfe' für eine Befehlsübersicht ein.")

    while True:
        try:
            user_input = await asyncio.to_thread(input, '> ')
            
            cleaned_input = user_input.strip()
            if cleaned_input.startswith('>'):
                cleaned_input = cleaned_input[1:].strip()

            if not cleaned_input:
                continue
            
            if cleaned_input.lower() == 'exit':
                print("Anwendung wird beendet.")
                break

            policy_ok, policy_data = await check_policy(cleaned_input, proc)
            if not policy_ok:
                reason = policy_data.get('reason', 'Policy check failed')
                await log_flight_record(proc, cleaned_input, 'denied', reason)
                print(f"Fehler: {reason}")
                continue

            result: Dict[str, str] = await proc.process(cleaned_input)
            await log_flight_record(
                proc,
                cleaned_input,
                policy_data.get('policy_status', 'approved'),
                result.get('result', ''),
            )

            if result.get('status') == 'success':
                print(result.get('result', ''))
            else:
                print(f"Fehler: {result.get('result', 'Unbekannter Fehler')}")

        except KeyboardInterrupt:
            print("\nAnwendung wird beendet.")
            break
        except Exception as e:
            logging.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}", exc_info=True)
            print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

async def check_policy(command: str, proc: CommandProcessor) -> (bool, Dict[str, Any]):
    config = proc.config
    url = getattr(config, 'policy_url', None)
    if not url:
        return True, {"policy_status": "skipped", "reason": "Policy URL not set"}

    payload = {
        "command": command,
        "context": {
            "user_role": "cli_user",
            "user_id": "local_cli",
        },
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=5) as resp:
                data = await resp.json()
                return data.get('policy_status') == 'approved', data
    except Exception as exc:
        logging.error("Policy check failed: %s", exc)
        return False, {"policy_status": "error", "reason": str(exc)}


async def log_flight_record(proc: CommandProcessor, command: str, policy_status: str, result: str) -> None:
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "command": command,
        "policy_status": policy_status,
        "result": result,
        "metadata": {"source": "cli-app"},
    }
    with open("flight_recorder.log", "a", encoding="utf-8") as fp:
        fp.write(json.dumps(entry) + "\n")

    url = getattr(proc.config, 'flight_recorder_url', None)
    if not url:
        return
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=entry, timeout=5)
    except Exception as exc:
        logging.error("Flight recorder push failed: %s", exc)

def run():
    """Startet die Anwendung."""
    global processor
    
    # Ermitteln des absoluten Pfads zur config.ini, die sich im selben Verzeichnis wie main.py befindet
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, 'config.ini')
    except NameError:
        # Fallback für Umgebungen, in denen __file__ nicht definiert ist (z.B. interaktive Interpreter)
        config_path = 'config.ini'

    config = Configuration(config_path)
    processor = CommandProcessor(config)
    
    web_thread = Thread(target=run_web_interface, daemon=True)
    web_thread.start()
    logging.info(f"Web-Interface gestartet auf http://127.0.0.1:5001")

    try:
        asyncio.run(main_loop(processor))
    except KeyboardInterrupt:
        logging.info("Anwendung durch Benutzer beendet.")
    finally:
        sys.exit(0)

if __name__ == '__main__':
    run()
