from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import html

app = Flask(__name__)
CORS(app)  # Erlaubt Anfragen von Ihrer Android-App

# In-memory "Flugschreiber"-Datenbank.
# In einer echten Anwendung wäre dies eine richtige Datenbank.
flight_logs = []

@app.route("/", methods=['POST'])
def policy_check():
    """Der primäre Endpunkt zur Ethik-Prüfung."""
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

@app.route("/log", methods=['POST'])
def flight_recorder():
    """
    Der 'Flugschreiber'-Endpunkt.
    Nimmt strukturierte Log-Daten von der Zelle entgegen und speichert sie.
    """
    log_data = request.get_json(silent=True)
    if not log_data:
        return jsonify({"status": "error", "message": "Keine Log-Daten erhalten"}), 400

    log_data['server_timestamp'] = datetime.datetime.utcnow().isoformat()
    flight_logs.append(log_data)
    print(f"FLIGHT_RECORDER_LOG: {log_data}") # Optional: weiterhin im Server-Log ausgeben

    return jsonify({"status": "logged"}), 200

@app.route("/show_logs", methods=['GET'])
def show_logs():
    """Zeigt alle 'Flugschreiber'-Einträge als einfache HTML-Seite an."""
    html_output = "<h1>Flugschreiber - Ethische Voice Cell</h1>"
    html_output += f"<p>Anzahl der Einträge: {len(flight_logs)}</p>"
    html_output += "<table border='1' style='width:100%; border-collapse: collapse;'>"
    html_output += "<tr><th>Server-Zeit</th><th>Client-Zeit</th><th>Typ</th><th>Quelle</th><th>Payload</th><th>Entscheidung</th></tr>"

    # Zeige die neuesten Logs zuerst an
    for log in reversed(flight_logs):
        html_output += "<tr>"
        html_output += f"<td>{html.escape(log.get('server_timestamp', 'N/A'))}</td>"
        html_output += f"<td>{html.escape(log.get('clientTimestamp', 'N/A'))}</td>"
        html_output += f"<td>{html.escape(log.get('eventType', 'N/A'))}</td>"
        html_output += f"<td>{html.escape(log.get('source', 'N/A'))}</td>"
        html_output += f"<td>{html.escape(log.get('payload', 'N/A'))}</td>"
        html_output += f"<td>{html.escape(log.get('decision', 'N/A'))}</td>"
        html_output += "</tr>"

    html_output += "</table>"
    return html_output

