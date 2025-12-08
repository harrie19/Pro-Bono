"""Minimal flight recorder service for the CLI + Android."""
from datetime import datetime
import logging
import os
import json
from pathlib import Path
from typing import Dict, Any

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def _persist(entry: Dict[str, Any]) -> None:
    target = Path(os.environ.get("FLIGHT_RECORDER_LOG", "flight_recorder.log"))
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(entry) + "\n")

@app.post('/flight_record')
def record_event():
    payload = request.json or {}
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "command": payload.get("command", ""),
        "policy_status": payload.get("policy_status", "unknown"),
        "result": payload.get("result", ""),
        "metadata": payload.get("metadata", {}),
    }
    logging.info("Flight record: %s", entry)
    _persist(entry)
    return jsonify({"status": "recorded"}), 200

@app.get('/health')
def health():
    return jsonify({"status": "healthy", "service": "flight-recorder"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8090)
