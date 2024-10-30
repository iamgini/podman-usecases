from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with your secret key
socketio = SocketIO(app)

# Global variable to store status data
data_store = {
    "status_data": {}
}

@app.route('/')
def index():
    return "WebSocket server is running!"

@app.route('/update_data', methods=['POST'])
def update_data():
    global data_store
    # Assume the incoming data is JSON
    new_data = request.json

    # Clear the existing data_store and update it with the new data
    data_store = new_data  # Update the entire structure

    # Send updates to all connected clients
    send_updates()

    return jsonify({"status": "success", "data": new_data})

def send_updates():
    # Emit the updated data to all connected clients
    socketio.emit('update', data_store)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('update', data_store)  # Send the current data when a new client connects

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
