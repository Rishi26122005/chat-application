from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

# 1. Handle a user joining a specific chat room
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    print(f"{username} joined room: {room}")
    # Notify only people in that specific room
    emit('status', {'msg': f"{username} has joined the chat."}, to=room)

# 2. Handle a user leaving a room (when switching chats)
@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f"{username} has left the chat."}, to=room)

# 3. Route messages ONLY to the target room
@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    print(f"[{room}] {data['username']}: {data['text']}")
    # 'to=room' ensures ONLY members of this room receive the message
    emit('receive_message', data, to=room)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)