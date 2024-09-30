from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<room_id>')
def room(room_id):
    return render_template('room.html', room_id=room_id)

@socketio.on('connect')
def handle_connect():
    print('1')
    room_id = request.path[1:]  # Extract room ID from the URL
    join_room(room_id)
    print(f"User connected to room: {room_id}")
    #socketio.emit('message', {'msg': 'Welcome to the chat!', 'room': room_id}, room=room_id)

@socketio.on('join')  # Handle the 'join' event
def handle_join(data):
    room_id = data.get('room')
    join_room(room_id)
    print(f"User joined room: {room_id}")
    #socketio.emit('message', {'msg': 'Welcome to the chat!', 'room': room_id}, room=room_id)

@socketio.on('message')
def handle_message(data):
    print('2')
    room_id = data.get('room')
    message = data.get('msg')
    print(f"Message in room {room_id}: {message}")
    socketio.emit('message', {'msg': message, 'room': room_id}, room=room_id)

@socketio.on('disconnect')
def handle_disconnect():
    print('3')
    room_id = request.path[1:]
    leave_room(room_id)
    print(f"User disconnected from room: {room_id}")

if __name__ == '__main__':
    socketio.run(app, debug=True)
