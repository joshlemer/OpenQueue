import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask.ext.script import Manager, Server, Command
from __init__ import app

manager = Manager(app)

# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger = True,
    use_reloader = True,
    host = '0.0.0.0')
)


class PopulateDatabase(Command):
	def run(self):
		import database_script


manager.add_command("repopulate", PopulateDatabase())

if __name__ == "__main__":
    manager.run()

