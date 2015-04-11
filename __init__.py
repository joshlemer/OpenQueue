from flask import Flask
from flask.ext.mongoengine import MongoEngine
from pymongo import read_preferences

app = Flask(__name__)

app.config["MONGODB_SETTINGS"] = {'db': 'qme'}
app.config['SECRET_KEY'] = 'password'
app.config['read_preference'] = read_preferences.ReadPreference.PRIMARY

db = MongoEngine(app)

if __name__ == '__main__':
	app.run()

def register_blueprints(app):
    # Prevents circular imports
    from qme_src.views import rooms
    app.register_blueprint(rooms)

register_blueprints(app)
