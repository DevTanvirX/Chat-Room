from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit
from datetime import datetime
from werkzeug.utils import escape

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Store messages temporarily for persistence
messages = []  # List to store messages temporarily
active_users = {}  # Dictionary to store users in each room

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    username = escape(data['username'])
    room = escape(data['room'])
    join_room(room)
    
    # Add user to the active users list
    active_users.setdefault(room, []).append(username)
    
    # Send user list to the room
    emit('user_list', {'users': active_users[room]}, room=room)
    
    # Send last 10 messages to the new user
    emit('message_history', messages[-10:], room=request.sid)
    
    emit('system_message', {'message': f'{username} has joined the room.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    username = escape(data['username'])
    room = escape(data['room'])
    leave_room(room)
    
    # Remove user from the active users list
    active_users[room].remove(username)
    emit('user_list', {'users': active_users[room]}, room=room)
    
    emit('system_message', {'message': f'{username} has left the room.'}, room=room)

@socketio.on('send_message')
def handle_send_message(data):
    message = escape(data['message'])
    username = escape(data['username'])
    room = escape(data['room'])
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    # Store message for persistence
    messages.append({'message': message, 'username': username, 'timestamp': timestamp, 'room': room})

    # Emit message to the room
    emit('receive_message', {'message': message, 'username': username, 'timestamp': timestamp}, room=room)

@socketio.on('send_file')
def handle_send_file(data):
    emit('receive_file', {'file': data['file'], 'filename': data['filename'], 'username': data['username'], 'timestamp': datetime.now().strftime('%H:%M:%S')}, room=data['room'])

@socketio.on('typing')
def handle_typing(data):
    username = escape(data['username'])
    room = escape(data['room'])
    emit('typing', {'username': username}, room=room)

@socketio.on('stop_typing')
def handle_stop_typing(data):
    room = escape(data['room'])
    emit('stop_typing', room=room)

if __name__ == '__main__':
    from gevent import monkey
    monkey.patch_all()
    socketio.run(app, host='0.0.0.0', port=3000)
