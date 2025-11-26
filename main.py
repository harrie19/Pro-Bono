from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Erlaubt Anfragen von Ihrer Android-App

@app.route("/", methods=['POST'])
def policy_check():
    request_json = request.get_json(silent=True)

    if not request_json or 'command' not in request_json:
        return jsonify({"status": "error", "message": "Ungültige Anfrage"}), 400

    command = request_json['command']

    if "malware" in command.lower():
        response_data = {
            "status": "policy_violation",
            "message": "Aktion abgelehnt: Der Befehl verstößt gegen die Sicherheitsrichtlinien."
        }
    else:
        response_data = {
            "status": "policy_compliant",
            "message": "Aktion ist Policy-konform und wird ausgeführt."
        }

    return jsonify(response_data)
