from flask_socketio import send, emit
from flask import Flask, render_template
from flask_socketio import SocketIO
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@socketio.on('message')
def handle_message(message):
    send(message)


if __name__ == '__main__':
    t = threading.Thread(target=socketio.run, args=(app, ))
    t.start()
    handle_message('123')
