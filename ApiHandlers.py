import flask_restful
from flask import abort
from models import *
from flask.ext.login import current_user


class RoomApi(flask_restful.Resource):
	def get(self, slug):
		room = Room.objects(slug=slug).first()
		if room:
			return room.to_json_dict()
		abort(404)

	def post(self):
		return "foo post"


class JoinQueueApi(flask_restful.Resource):
	def post(self, queue_slug):
		queue = Queue.objects(slug=queue_slug).first()
		if current_user.is_authenticated() and queue:
			queue_element = QueueElement(user=User.objects(email=current_user.email).first(), accepts=queue.resources)
			queue_element.save()
			queue.add_queue_element(queue_element)
			queue.save()

class RoomsListApi(flask_restful.Resource):
	def get(self):
		return [{
			'name': room.name,
			'_id': str(room.id),
			'slug': room.slug
		} for room in Room.objects]


class QueueElementApi(flask_restful.Resource):
	def delete(self, queue_id, queue_element_id):
		queue = Queue.objects(id=queue_id).first()
		queue_element = QueueElement.objects(id=queue_element_id).first()
		if current_user.is_authenticated() and current_user.id == queue_element.user.id and queue:
			queue.remove_queue_element(queue_element)


