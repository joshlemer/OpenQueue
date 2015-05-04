import flask_restful
from flask import abort, request
from models import *
from flask.ext.login import current_user
import ast
import json


class RoomApi(flask_restful.Resource):
	def get(self, slug):
		room = Room.objects(slug=slug).first()
		if room:
			result = room.to_json_dict()
			if room.owner and room.owner.id == current_user.id:
				result['isOwner'] = True
			else:
				result['isOwner'] = False
			return result
		abort(404)


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

	def post(self):

		if request.data:
			request_data = ast.literal_eval(request.data)
			data = request_data.get('data')
			if data.get('name') and current_user.is_authenticated():
				new_room = Room(name=data['name'], owner=User.objects(id=current_user.id).first())
				new_room.save()

class QueueApi(flask_restful.Resource):
	def post(self, slug):
		if request.data:
			request_data = ast.literal_eval(request.data)
			data = request_data.get('data')
			room = Room.objects(slug=slug).first()
			if data.get('name') and current_user.is_authenticated() and room and room.owner.id == current_user.id:
				new_queue = Queue(name=data['name'], room=room)
				new_queue.save()
				room.queues.append(new_queue)
				room.save()

class EditQueueApi(flask_restful.Resource):
	def post(self, slug, queue_id):
		if request.data:
			data = json.loads(request.data).get('data')
			room = Room.objects(slug=slug).first()
			queue = Queue.objects(id=queue_id).first()
			if room and queue and data.get('name') and current_user.is_authenticated() and room.owner.id==current_user.id:
				queue_name = data.get('name')
				resources = data.get('resources')
				deleted_resource_ids = data.get('deletedResources')

				if queue_name:
					queue.name = queue_name

				for resource in resources:
					id = resource.get('_id')
					resource_name = resource.get('name') if resource.get('name') else 'Untitled'
					if id:
						the_resource = Resource.objects(id=id).first()
					if id and the_resource:
						the_resource.name = resource_name
						the_resource.save()
					elif not id:
						the_resource = Resource(name=resource_name)
						the_resource.save()
						queue.resources.append(the_resource)

				queue.save()

				if deleted_resource_ids:
					for resource in queue.resources:
						if str(resource.id) in deleted_resource_ids:
							resource.delete()





	def delete(self, slug, queue_id):
		queue = Queue.objects(id=queue_id).first()
		if current_user.is_authenticated() and queue:
			queue.delete()


class QueueElementApi(flask_restful.Resource):
	def delete(self, queue_id, queue_element_id):
		queue = Queue.objects(id=queue_id).first()
		queue_element = QueueElement.objects(id=queue_element_id).first()
		if current_user.is_authenticated() and queue_element and current_user.id == queue_element.user.id and queue:
			queue.remove_queue_element(queue_element)
			queue_element.delete()


