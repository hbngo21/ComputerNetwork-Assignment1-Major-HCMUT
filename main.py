from flask import Flask, render_template
import eventlet
import socketio
from eventlet import wsgi
import base64
from VideoStream import VideoStream

INIT = 0
READY = 1
PLAYING = 2

state = {}

app = Flask(__name__)
server = socketio.Server()
app.wsgi_app = socketio.WSGIApp(server, app.wsgi_app)

@app.route('/')
def index():
    return render_template('index.html')

@server.event
def connect(id, environ=None, auth=None):
    global state
    state[id] = INIT

@server.on("SETUP")
def setup(id):
    global state, video
    state[id] = READY
    video = VideoStream('movie.Mjpeg')

@server.on("PLAY")
def play(id):
    global state
    if state[id] == READY:
        i = 0
        state[id] = PLAYING
        while state[id] == PLAYING:
            frame = video.nextFrame()
            if frame:
                frame= base64.encodebytes(frame).decode("utf-8")
                i += 1
                server.emit("response", frame)
                server.sleep(0.04)
            else:
                state[id] = READY
                
@server.on("PAUSE")
def pause(id):
    global state
    state[id] = READY

@server.event
def disconnect(id):
    print("Disconnected from the server!")

if __name__ == '__main__':
    wsgi.server(eventlet.listen(('127.0.0.1',3000)), app)
    



