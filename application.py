import os
import time
from flask import Flask, render_template, redirect, url_for, flash,request
from flask_login import LoginManager , login_user, current_user , logout_user
from flask_socketio import SocketIO, send, join_room,leave_room

from wtforms_fields import *
from models import *


# Configure App
app = Flask(__name__)
app.secret_key = 'replace later'

#Configure database
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://phzslmnqktoayb:c68a6d5b59a9709d7d254ca627bc999c8b5b23e11b7c47e8b25f2869ccb8fbaf@ec2-3-208-79-113.compute-1.amazonaws.com:5432/d8h8lveblshgp0'
db= SQLAlchemy(app)


# Initialize login manager
login = LoginManager(app)
login.init_app(app)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# Initialize Flask-SocketIO
socketio = SocketIO(app, manage_session=False)
ROOMS = ["lounge","news","games","coding"]


# Configure flask login 
login = LoginManager(app)
login.init_app(app)


@login.user_loader
def load_user(id):

    return User.query.get(int(id))

@app.route("/", methods=['GET', 'POST'])
def index():

    # update database if validation seccess
    reg_form= RegistrationForm()
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data
        
        hashed_pswd = pbkdf2_sha256.hash(password)

        # Add user to database
        user = User(username=username, password=hashed_pswd)
        db.session.add(user)
        db.session.commit()

        flash('Registered Succesfully. Please login.','success')

        return redirect(url_for('login'))

    return render_template("index.html", form=reg_form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    
    login_form = LoginForm()

    #Allow login if validation success
    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username=login_form.username.data).first()
        login_user(user_object)
        return redirect(url_for('chat'))
        
        return "Not Loggedin"    

    return render_template("login.html",form = login_form)

@app.route("/chat", methods=['GET','POST'])
# @login_required
def chat():

            if not current_user.is_authenticated:
                flash('Please login.','danger')
                return redirect(url_for('login'))
            
            return render_template('chat.html',username=current_user.username,rooms=ROOMS)


@app.route("/logout", methods=['GET'])
def logout():

    logout_user()
    flash('You have logout succesfully.','success')
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@socketio.on('incoming-msg')
def on_message(data):
    """Broadcast messages"""

    msg = data["msg"]
    username = data["username"]
    room = data["room"]
    # Set timestamp
    time_stamp = time.strftime('%b-%d %I:%M%p', time.localtime())
    send({"username": username, "msg": msg, "time_stamp": time_stamp}, room=room)


@socketio.on('join')
def join(data):
    """User joins a room"""

    username = data["username"]
    room = data["room"]
    join_room(room)
# Broadcast that new user has joined
    send({"msg": username + " has joined the " + room + " room."}, room=room)


@socketio.on('leave')
def leave(data):
    """User leaves a room"""

    username = data['username']
    room = data['room']
    leave_room(room)
    send({"msg": username + " has left the room"}, room=room)

if __name__ =="__main__":
    socketio.run(app,debug=True,allow_unsafe_werkzeug=True) 