import flask_restful
from flask import abort
from models import *
from flask.ext.login import current_user
import ast


class RoomApi(flask_restful.Resource):
	def get(self, slug):
		room = Room.objects(slug=slug).first()
		if room:

			# return User.objects(email='joshlemer@gmail.com').first().to_json_dict()
			return room.to_json_dict()
			return ast.literal_eval(room.to_json())
		abort(404)

	def post(self):
		return "foo post"


class JoinQueueApi(flask_restful.Resource):
	def post(self, room_slug, queue_name):
		room = Room.objects(slug=room_slug).first()
		if current_user and room:
			queues = [q for q in room.queues if q.name == queue_name]
			if len(queues):
				queue = queues[0]
			else:
				queue = None

			if queue:
				queue_element = QueueElement(user=User.objects(email=current_user.email).first(), accepts=queue.resources)
				queue.add_queue_element(queue_element)
				room.save()


