from flask import Flask, render_template, request, session as flask_session, g, send_from_directory, redirect, url_for
#from flask.ext.socketio import SocketIO, emit, send
from flask_socketio import SocketIO, emit, send
import model
import os
import datetime

UPLOAD_FOLDER = 'static/img'

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# should probably hide this secret key at some point?
app.config['SECRET_KEY'] = 'TROLOLOLOLOLO!'
socketio = SocketIO(app)

@app.before_request
def global_variables():
    if "user" in flask_session:
        g.user_id = flask_session["user"]["id"]
        g.username = flask_session["user"]["username"]
        #return 'OK'

@app.route('/canvas', methods=['GET', 'POST'])
def sign_up_log_in():
    if request.method == 'GET':
        return render_template('index.html')
    #----------------------------------------------------------------------
    # Find way to prevent modal from popping up if user already in session.
    #----------------------------------------------------------------------
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = model.get_user_by_username(username)

        if user == None:
            model.save_user_to_db(username, password)
            return "Oke Sip"
        else:
            if user.password == password:
                flask_session["user"] = {"username":user.username, "id":user.id}
                return "Oke Sip"
            else:
                return "blm NOO"

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Tidak boleh. Mohon coba lagi'
        else:
            return redirect(url_for('sign_up_log_in'))
    return render_template('login.html', error = error)
                
@app.route('/save', methods=['POST'])
def save_image():
    img = request.files['image']
    if img:
        # mac version below
        # filename = g.username + ".png"
        # fullpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # Windows version below -- unsure why there is a difference between mac/windows
        dateObj = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        fullpath = app.config['UPLOAD_FOLDER'] + "/" + dateObj + ".png"
        img.save(fullpath)
        image = model.get_image_by_user_id(1)

        if image == None:
            model.save_image_to_db(1, fullpath)
            return "Image URL entered into database."
        else:
            return 'OK'


    return "Failure"

@socketio.on('broadcastImage')
def broadcast_image(data):
    emit('loadImage', data, broadcast=True)

@socketio.on('reset')
def reset(data):
    print("Reset")
    emit('resetCanvas', data, broadcast=True)

# Offers the load() javascript function the path it needs
@app.route('/static/img/<path:path>')
def send_user_image(path):
    return send_from_directory('static/img', path)

@socketio.on('connection')
def listen_send_all(data):
    emit('new user')

@socketio.on('mousemove')
def brdcast_moving(data):
    emit('moving', data, broadcast=True)

@socketio.on('mouseup')
def brdcast_stop(data):
    emit('stopping', data, broadcast=True)

@socketio.on('broadcastColor')
def brdcast_color(data):
    emit('strokeColor', data, broadcast=True)

@socketio.on('deleteUnloaded')
def delete_unloaded(data):
    emit('deleteRemoteUser', data, broadcast=True)

PORT=int(os.environ.get("PORT", 5000))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=PORT)
