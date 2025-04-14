import os
import json
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
WELCOME_MESSAGE = os.environ.get('WELCOME_MESSAGE', 'Welcome to the custom app')
PORT = int(os.environ.get('PORT', 5000))
LOG_FILE = '/app/logs/app.log'

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

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

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open(LOG_FILE, 'r') as f:
            logs = f.read()
        return logs
    except FileNotFoundError:
        return "No logs found", 404

if __name__ == '__main__':
    print(f"Starting application on port {PORT} with log level {LOG_LEVEL}")
    app.run(host='0.0.0.0', port=PORT)