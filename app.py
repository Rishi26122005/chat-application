from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Database Model for Storing Messages Permanently
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create the SQLite database file automatically if it doesn't exist
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    print(f"{username} joined room: {room}")
    
    # 1. Fetch past messages for this room from SQLite database
    past_messages = ChatMessage.query.filter_by(room=room).order_by(ChatMessage.timestamp.asc()).all()
    history = [{
        'username': msg.username, 
        'text': msg.text, 
        'timestamp': msg.timestamp.strftime('%H:%M')
    } for msg in past_messages]
    
    # 2. Send history ONLY to the user who just joined
    emit('load_history', history)
    
    # 3. Notify the rest of the room
    emit('status', {'msg': f"{username} has joined the chat."}, to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f"{username} has left the chat."}, to=room)

@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    username = data['username']
    text = data['text']
    
    # Save the new message to the SQLite database
    new_msg = ChatMessage(room=room, username=username, text=text)
    db.session.add(new_msg)
    db.session.commit()
    
    timestamp_str = new_msg.timestamp.strftime('%H:%M')
    payload = {
        'username': username, 
        'room': room, 
        'text': text, 
        'timestamp': timestamp_str
    }
    
    # Broadcast message and timestamp to everyone in the room
    emit('receive_message', payload, to=room)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)