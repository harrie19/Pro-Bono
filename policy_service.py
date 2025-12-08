"""Minimal Flask-based policy check service.

Run with:
    FLASK_ENV=production python policy_service.py
"""
from datetime import datetime
import logging
from typing import Dict, Any

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

ALLOWED_COMMAND_PREFIXES = ("analyse", "lesen", "speichern", "zeit", "hilfe", "wetter")
BLOCKED_PATTERNS = ["rm -rf", "drop table", "delete from", "chmod 777", "curl | bash"]


def _evaluate_command(command: str, context: Dict[str, Any]) -> Dict[str, Any]:
    command_lower = command.lower()
    status = "approved"
    reason = "Command approved"

    for pattern in BLOCKED_PATTERNS:
        if pattern in command_lower:
            status = "denied"
            reason = f"Blocked pattern detected: {pattern}"
            break

    if status == "approved":
        role = context.get("user_role", "guest")
        if role == "guest" and any(k in command_lower for k in ("delete", "rm", "drop")):
            status = "denied"
            reason = "Guests are not allowed to run destructive commands"

    return {
        "policy_status": status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "command": command,
        "reason": reason,
        "metadata": {
            "service": "policy-check-flask",
            "checked_at": datetime.utcnow().isoformat() + "Z",
            "user_role": context.get("user_role", "guest"),
        },
    }


@app.post("/policy_check")
def policy_check():
    payload: Dict[str, Any] = request.json or {}
    command: str = payload.get("command", "")
    context: Dict[str, Any] = payload.get("context", {})

    if not command:
        return jsonify({"policy_status": "error", "reason": "Missing command"}), 400

    decision = _evaluate_command(command, context)
    logging.info("Policy check %s for command '%s'", decision["policy_status"], command[:80])
    return jsonify(decision)


@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "policy-check"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)

