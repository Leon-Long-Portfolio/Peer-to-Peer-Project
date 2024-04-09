from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import threading

app = Flask(__name__)

# In-memory storage of online users
online_users = {}
users_lock = threading.Lock()

# Extend code to allow registration
@app.route('/register', methods=['POST'])
def register():
    user_id = request.json.get('user_id')
    address = request.json.get('address')
    with users_lock:
        online_users[user_id] = (address, datetime.utcnow())
    return jsonify({"success": True})

# Keep alive for online
@app.route('/keepalive', methods=['POST'])
def keep_alive():
    user_id = request.json.get('user_id')
    with users_lock:
        if user_id in online_users:
            address, _ = online_users[user_id]
            online_users[user_id] = (address, datetime.utcnow())
            return jsonify({"success": True})
        else:
            return jsonify({"error": "User not registered"}), 404

# Look up users
@app.route('/lookup/<user_id>', methods=['GET'])
def lookup(user_id):
    with users_lock:
        user_info = online_users.get(user_id)
        if user_info:
            address, last_seen = user_info
            is_online = datetime.utcnow() - last_seen < timedelta(minutes=5)
            return jsonify({"address": address, "online": is_online, "last_seen": last_seen.isoformat()})
        else:
            return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=4900)
