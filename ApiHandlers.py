import flask_restful
from flask import abort, request
from models import *
from flask.ext.login import current_user
import ast
import json

class HomeApi(flask_restful.Resource):
	def get(self):
		if current_user.is_authenticated():
			user = User.objects(id=current_user.id).first()

			if user:
				user_owned_rooms = Room.objects(owner__in=[user])
				user_member_rooms = Room.objects(members__in=[user])
				user_starred_rooms = user.starred_rooms

				return {
					'owned_rooms': [
						{
						'name': r.name,
						'slug': r.slug
						}
						for r in user_owned_rooms],
					'memberships': [
						{
						'name': r.name,
						'slug': r.slug
						}
						for r in user_member_rooms],
					'starred_rooms': [
						{
							'name': r.name,
							'slug': r.slug
						}
						for r in user_starred_rooms]
				}

		return {}


class RoomApi(flask_restful.Resource):
	def get(self, slug):

		room = Room.objects(slug=slug).first()

		if current_user.is_authenticated():
			user = User.objects(id=current_user.id).first()
		else:
			user = None

		if room and (room.is_public or user==room.owner or  user in room.members):
			result = room.to_json_dict()
			if current_user.is_authenticated():
				if room.owner and room.owner.id == current_user.id:
					result['isOwner'] = True
				else:
					result['isOwner'] = False
				if room.members and user and user in room.members:
					result['isMember'] = True
				else:
					result['isMember'] = False
				if room in user.starred_rooms:
					result['isStarred'] = True
				else:
					result['isStarred'] = False

			else:
				result['isOwner'] = False
				result['isMember'] = False

			return result
		abort(404)

	def delete(self, slug):
		room = Room.objects(slug=slug).first()
		if room and current_user.is_authenticated() and room.owner.id==current_user.id:
			room.delete()

	def post(self, slug):
		if request.data:
			data = json.loads(request.data).get('data')
			room = Room.objects(slug=slug).first()
			if room and current_user.is_authenticated() and room.owner.id==current_user.id:
				room_name = data.get('name')
				new_members = data.get('newMembers')
				deleted_member_ids = data.get('deletedMembers')
				is_public = data.get('is_public')

				if room_name:
					room.name = room_name

				if new_members:
					for new_member in new_members:
						user = User.objects(email=new_member.get('email')).first()
						if user and user != room.owner and user not in room.members:
							room.members.append(user)
							room.save()

				if deleted_member_ids:
					for deleted_member_id in deleted_member_ids:
						user = User.objects(id=deleted_member_id).first()
						if user:
							room.update(pull__members=user)

				if is_public != None:
					room.is_public = is_public

				room.save()


class LeaveRoomApi(flask_restful.Resource):
	def post(self, slug):
		if current_user.is_authenticated():
			user = User.objects(id=current_user.id).first()
			room = Room.objects(slug=slug).first()
			if user and room:
				room.members.remove(user)
				room.save()

class StarRoomApi(flask_restful.Resource):
	def post(self, slug):
		if current_user.is_authenticated():
			user = User.objects(id=current_user.id).first()
			room = Room.objects(slug=slug).first()
			if user and room:
				if room in user.starred_rooms:
					user.starred_rooms.remove(room)
					pass
				else:
					user.starred_rooms.append(room)
				user.save()

class JoinQueueApi(flask_restful.Resource):
	def post(self, queue_id):
		queue = Queue.objects(id=queue_id).first()

		#Default to no description and accept all resources
		accepts = queue.resources
		description = ''

		if request.data:
			data = json.loads(request.data).get('data')
			if data.get('accepts'):
				accepts = Resource.objects(id__in=data.get('accepts'))
				accepts = [a for a in accepts if a in queue.resources]
			if data.get('description'):
				description = data.get('description')

		if current_user.is_authenticated() and queue:
			queue_element = QueueElement(user=User.objects(id=current_user.id).first(), accepts=accepts, description=description)
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
					resource_is_active = resource.get('is_active')

					if id:
						the_resource = Resource.objects(id=id).first()
					if id and the_resource:
						the_resource.name = resource_name
						if resource_is_active is not None:
							the_resource.is_active = resource_is_active
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

				queue.flush_queue()


	def delete(self, slug, queue_id):
		queue = Queue.objects(id=queue_id).first()
		if current_user.is_authenticated() and queue and queue.room and queue.room.owner.id==current_user.id:
			queue.delete()


class QueueElementApi(flask_restful.Resource):
	def delete(self, queue_id, queue_element_id):
		queue = Queue.objects(id=queue_id).first()
		queue_element = QueueElement.objects(id=queue_element_id).first()
		if current_user.is_authenticated() and queue_element and (current_user.id == queue_element.user.id or current_user.id == queue.room.owner.id) and queue:
			queue.remove_queue_element(queue_element)
			queue_element.delete()

	def post(self, queue_id, queue_element_id):
		if request.data:
			data = json.loads(request.data).get('data')
			queue = Queue.objects(id=queue_id).first()
			queue_element = QueueElement.objects(id=queue_element_id).first()
			if request.data and current_user.is_authenticated() and queue_element and current_user.id == queue_element.user.id and queue:
				description = data.get('description')
				if description:
					queue_element.description = description
					queue_element.save()


