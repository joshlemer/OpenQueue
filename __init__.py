import os
from flask import Flask, flash, render_template, redirect, session, url_for, request, get_flashed_messages, make_response
from flask.ext.mongoengine import MongoEngine, MongoEngineSessionInterface
from flask.ext.login import LoginManager, UserMixin, current_user, login_user, logout_user
from flask.ext.bcrypt import Bcrypt
from pymongo import read_preferences
from flask_restful import Api

app = Flask(__name__)
bcrypt = Bcrypt(app)
api = Api(app)

MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
	MONGO_URL = 'mongodb://localhost:27017/qme'

app.config['MONGO_URI'] = MONGO_URL
app.config["MONGODB_SETTINGS"] = {'db': 'qme'}
app.config['SECRET_KEY'] = 'password'
app.config['read_preference'] = read_preferences.ReadPreference.PRIMARY

db = MongoEngine(app)
app.session_interface = MongoEngineSessionInterface(db)

flask_bcrypt = Bcrypt(app)

from ApiHandlers import *
api.add_resource(RoomApi, '/api/rooms/<slug>/')
api.add_resource(JoinQueueApi, '/api/queues/<queue_id>/join/')
api.add_resource(RoomsListApi, '/api/rooms/')
api.add_resource(QueueElementApi, '/api/queues/<queue_id>/queue_elements/<queue_element_id>/')
api.add_resource(QueueApi, '/api/rooms/<slug>/queues/')
api.add_resource(EditQueueApi, '/api/rooms/<slug>/queues/<queue_id>/')

if __name__ == '__main__':
	app.run()

def register_blueprints(app):
	# Prevents circular imports
	from views import rooms
	app.register_blueprint(rooms)


register_blueprints(app)

login_manager = LoginManager(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
	from models import User
	return User.objects(id=user_id).first()


@app.route('/login')
def login():
	return render_template('login.html', request=request)


@app.route('/login/check', methods=['post'])
def login_check():
	# validate username and password
	#user = User.get(request.form['username'])
	from models import User
	user = User.objects(email=request.form['email']).first()
	pw_check = bcrypt.check_password_hash(user.password , request.form['password'] )
	if (user and pw_check):
		login_user(user, remember=True)
	else:
		flash('Username or password incorrect')
		return redirect(url_for('login'))

	resp = make_response(redirect('/'))
	resp.set_cookie('userId', str(current_user.id))

	return resp

@app.route('/logout')
def logout():
	logout_user()
	resp = make_response(redirect('/'))
	resp.set_cookie('userId', '')
	return resp

@app.route('/signup', methods=['GET'])
def getSignup():
	return render_template('signup.html', request=request)

@app.route('/signup', methods=['POST'])
def postSignup():
	from models import User
	first_name, last_name = request.form['first_name'], request.form['last_name']
	email, password, confirm_password = request.form['email'], request.form['password'], request.form['confirm_password']
	validated = True

	if (not first_name) or len(first_name) > 35:
		flash('First names must be between 1 and 35 characters.')
		validated = False
	if (not last_name) or len(last_name) > 35:
		flash('Last names must be between 1 and 35 characters.')
		validated = False
	if (not email) or len(email) > 50 or len(email) < 5:
		flash('Email Addresses must be between 5 and 50 characters')
		validated = False
	if email and User.objects(email=email).count() > 0:
		flash('A user with that email already exists')
		validated = False

	pw_hash = bcrypt.generate_password_hash(password)
	pw_check = bcrypt.check_password_hash(pw_hash, confirm_password)

	if not pw_check:
		flash("Your passwords didn't check out")
		validated = False

	if validated:
		new_user = User(first_name=first_name, last_name=last_name, email=email, password = pw_hash)
		new_user.save()
		login_user(new_user, remember=True)
		return redirect('/')

	return redirect('/signup')

@app.route('/404', methods=['GET'])
def get404():
	return render_template('404.html')
