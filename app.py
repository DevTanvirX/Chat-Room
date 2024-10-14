from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Route to render the index.html
@app.route('/')
def index():
    return render_template('index.html')

# Handle users joining a chat room
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('system_message', {'message': f'{username} has joined the room.'}, room=room)

# Handle users leaving a chat room
@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('system_message', {'message': f'{username} has left the room.'}, room=room)

# Handle sending a message
@socketio.on('send_message')
def handle_send_message(data):
    message = data['message']
    username = data['username']
    room = data['room']
    timestamp = datetime.now().strftime('%H:%M:%S')
    emit('receive_message', {'message': message, 'username': username, 'timestamp': timestamp}, room=room)

# Handle typing indicator
@socketio.on('typing')
def handle_typing(data):
    username = data['username']
    room = data['room']
    emit('typing', {'username': username}, room=room)

# Handle stopping typing indicator
@socketio.on('stop_typing')
def handle_stop_typing(data):
    room = data['room']
    emit('stop_typing', room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
