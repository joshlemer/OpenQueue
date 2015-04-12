from flask import Flask, flash, render_template, redirect, session, url_for, request, get_flashed_messages
from flask.ext.mongoengine import MongoEngine, MongoEngineSessionInterface
from flask.ext.login import LoginManager, UserMixin, current_user, login_user, logout_user
from flask.ext.bcrypt import Bcrypt
from pymongo import read_preferences
#from users import *

app = Flask(__name__)

app.config["MONGODB_SETTINGS"] = {'db': 'qme'}
app.config['SECRET_KEY'] = 'password'
app.config['read_preference'] = read_preferences.ReadPreference.PRIMARY

db = MongoEngine(app)
app.session_interface = MongoEngineSessionInterface(db)

flask_bcrypt = Bcrypt(app)

if __name__ == '__main__':
	app.run()

def register_blueprints(app):
    # Prevents circular imports
    from qme_src.views import rooms
    app.register_blueprint(rooms)


register_blueprints(app)

login_manager = LoginManager(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
	from qme_src.models import User
	return User.objects.get(user_id=user_id)

@app.route('/hello/')
@app.route('/hello/<name>/')
def josh(name=None):
	from qme_src.models import Room
	roomString = ""
	rooms = Room.objects

	for room in rooms:
		roomString += str(room)
	return roomString
	# return "Hello %s" % name


class UserNotFoundError(Exception):
    pass


# Simple user class base on UserMixin
# http://flask-login.readthedocs.org/en/latest/_modules/flask/ext/login.html#UserMixin
class User(UserMixin):
    '''Simple User class'''
    USERS = {
        # username: password
        'john': 'love mary',
        'mary': 'love peter'
    }

    def __init__(self, id):
        if not id in self.USERS:
            raise UserNotFoundError()
        self.id = id
        self.password = self.USERS[id]

    @classmethod
    def get(self_class, id):
        '''Return user instance of id, return None if not exist'''
        try:
            return self_class(id)
        except UserNotFoundError:
            return None


@login_manager.user_loader
def load_user(id):
	from qme_src.models import User 
	return User.objects(user_id=id).first()

@app.route('/')
def index():
    return (
        '''
            <h1>Hello {1}</h1>
            <p style="color: #f00;">{0}</p>
            <p>{2}</p>
        '''.format(
            # flash message
            ', '.join([ str(m) for m in get_flashed_messages() ]),
            current_user.get_id() or 'Guest',
            ('<a href="/logout">Logout</a>' if current_user.is_authenticated()
                else '<a href="/login">Login</a>')
        )
    )


@app.route('/login')
def login():
	return render_template('login.html')
    # return '''
    #     <form action="/login/check" method="post">
    #         <p>Username: <input name="username" type="text"></p>
    #         <p>Password: <input name="password" type="password"></p>
    #         <input type="submit">
    #     </form>
    # '''


@app.route('/login/check', methods=['post'])
def login_check():
    # validate username and password
    #user = User.get(request.form['username'])
    from qme_src.models import User
    user = User.objects(email=request.form['username']).first()
    if (user and user.password == request.form['password']):
        login_user(user)
    else:
        flash('Username or password incorrect')
        return redirect(url_for('login'))

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# @app.route('/room/<slug>/')
# def room(slug):
# 	from qme_src.models import Room

# 	room = Room.objects.get(slug=slug)

# 	return room.name
