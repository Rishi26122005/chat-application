from flask import Flask, render_template
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'

# Initialize SocketIO with our Flask app
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

# Event listener for incoming messages
@socketio.on('message')
def handle_message(data):
    print(f"Message received: {data}")
    # broadcast=True sends the message to ALL connected clients, not just the sender
    send(data, broadcast=True)

if __name__ == '__main__':
    # Use socketio.run instead of app.run to enable WebSocket support
    socketio.run(app, debug=True, port=5000)