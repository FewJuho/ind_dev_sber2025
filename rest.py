import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from prometheus_client import Counter, Summary, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
WELCOME_MESSAGE = os.environ.get('WELCOME_MESSAGE', 'Welcome to the custom app')
PORT = int(os.environ.get('PORT', 5000))
LOG_FILE = '/app/logs/app.log'

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

REQUEST_COUNT = Counter(
    'log_requests_total',
    'Total number of calls to /log endpoint'
)

SUCCESS_COUNT = Counter(
    'log_requests_success_total',
    'Total number of successful log attempts'
)
FAILURE_COUNT = Counter(
    'log_requests_failure_total',
    'Total number of failed log attempts'
)

REQUEST_LATENCY = Summary(
    'log_request_processing_seconds',
    'Time spent processing /log requests'
)

@app.route('/', methods=['GET'])
def welcome():
    return WELCOME_MESSAGE

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "ok"})

@app.route('/log', methods=['POST'])
def log_message():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Missing 'message' field"}), 400
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hostname = os.environ.get('HOSTNAME', 'unknown')
    log_entry = f"{timestamp} - {hostname} - {LOG_LEVEL} - {data['message']}\n"
    
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry)
    
    return jsonify({"success": True, "message": "Log entry added"})

@app.route('/log', methods=['POST'])
def log_entry():
    REQUEST_COUNT.inc()
    start_time = datetime.now()

    try:
        data = request.get_json(force=True)
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "log": data.get("log"),
            "level": data.get("level", LOG_LEVEL)
        }
        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(entry) + "\n")

        SUCCESS_COUNT.inc()
        return jsonify({"success": True, "entry": entry}), 201

    finally:
        elapsed = (datetime.now() - start_time).total_seconds()
        REQUEST_LATENCY.observe(elapsed)

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open(LOG_FILE, 'r') as f:
            logs = f.read()
        return logs, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/metrics', methods=['GET'])
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    print(f"Starting application on port {PORT} with log level {LOG_LEVEL}")
    app.run(host='0.0.0.0', port=PORT)