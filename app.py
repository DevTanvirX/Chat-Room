# app.py
from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Store users and messages (temporary)
rooms = {}

# Render the main chat interface
@app.route('/')
def index():
    return render_template('index.html')

# Handle joining rooms (chats)
@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']

    # Create room if it doesn't exist
    if room not in rooms:
        rooms[room] = []
    
    join_room(room)
    send(f'{username} has joined the room.', to=room)

# Handle leaving rooms
@socketio.on('leave')
def handle_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(f'{username} has left the room.', to=room)

# Handle message sending
@socketio.on('message')
def handle_message(data):
    room = data['room']
    message = data['message']
    username = data['username']

    # Save message to room's message list
    rooms[room].append({'username': username, 'message': message})
    
    send(f'{username}: {message}', to=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
