import datetime, time
from flask import url_for
from qme_src import db, bcrypt
from bson import json_util, ObjectId
import ast
from slugify import UniqueSlugify

class User(db.Document):
	user_id = db.LongField(min_value=0)
	email = db.EmailField(unique=True)
	password = db.StringField(default=True)
	active = db.BooleanField(default=True)
	isAdmin = db.BooleanField(default=False)
	timestamp = db.DateTimeField(default=datetime.datetime.now())

	def __unicode__(self):
		return self.email

	def to_json_dict(self):
		data = self.to_mongo()
		data['_id'] = str(data['_id'])
		data['timestamp'] = time.mktime(data['timestamp'].timetuple())

		return data

	def is_active(self):
		return self.active
	def get_id(self):
		return self.id
	def is_authenticated(self):
		return True
	def set_password(self, plaintext_password):
		self.password = bcrypt.generate_password_hash(plaintext_password)
		self.save()

class QueueElement(db.Document):

	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	user = db.ReferenceField('User')
	accepts = db.ListField(db.ReferenceField('Resource'))

	def __unicode__(self):
		result = ''
		if self.user:
			result += self.user.email + ' '
		result += 'Accepts: '
		for acceptable in self.accepts:
			result += str(acceptable)
		return result

	def to_json_dict(self, follow_refs=True):
		data = self.to_mongo()
		data['_id'] = str(data['_id'])
		data['user'] = self.user.to_json_dict()
		data['created_at'] = time.mktime(data['created_at'].timetuple())
		if follow_refs:
			data['accepts'] = [ r.to_json_dict() for r in self.accepts ]
		else:
			data['accepts'] = [{'name': r.name, '_id': str(r.id)} for r in self.accepts]

		return data

class Resource(db.Document):
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	name = db.StringField(max_length=255, required=True)
	current_queue_element = db.ReferenceField('QueueElement', reverse_delete_rule=db.NULLIFY)

	def __unicode__(self):
		return self.name

	def to_json_dict(self):
		data = self.to_mongo()
		data['_id'] = str(data['_id'])
		data['created_at'] = time.mktime(data['created_at'].timetuple())
		if self.current_queue_element :
			data['current_queue_element'] =  self.current_queue_element.to_json_dict(follow_refs=False)

		return data

	def release(self):
		self.current_queue_element = None
		self.save()

	def remove_queue_element(self, queue_element):
		current_queue_element = self.current_queue_element
		if current_queue_element and current_queue_element.id == queue_element.id:
			self.update(unset__current_queue_element=1)

class Queue(db.Document):
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	name = db.StringField(max_length=255, required=True)
	slug = db.StringField(max_length=255, required=True)
	resources = db.ListField(db.ReferenceField('Resource'))
	room = db.ReferenceField('Room')
	queue_elements = db.ListField(db.ReferenceField('QueueElement', reverse_delete_rule=db.PULL))

	def __unicode__(self):
		return self.name

	def save(self, *args, **kwargs):
		self.slug = UniqueSlugify(uids=[q.slug for q in (self.room.queues if self.room else [] ) ])(self.name)
		super(Queue, self).save(*args, **kwargs)

	def to_json_dict(self):
		data = self.to_mongo()
		data['_id'] = str(self.id)
		data['created_at'] = time.mktime(data['created_at'].timetuple())
		data['resources'] = [ r.to_json_dict() for r in self.resources ]
		data['queue_elements'] = [ qe.to_json_dict() for qe in self.queue_elements ]

		return data

	def add_queue_element(self, queue_element):
		self.queue_elements.append(queue_element)
		self.save()
		self.flush_queue()

	def remove_queue_element(self, queue_element):
		if queue_element in self.queue_elements:
			self.queue_elements.remove(queue_element)
			self.save()
		else:
			for resource in self.resources:
				resource.remove_queue_element(queue_element)
		self.flush_queue()

	def flush_queue(self):
		for queue_element in self.queue_elements:
			for resource in queue_element.accepts:
				if resource.current_queue_element is None:
					resource.current_queue_element = queue_element
					resource.save()
					self.queue_elements.remove(queue_element)
					self.save()
					break


class Room(db.Document):
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	name = db.StringField(max_length=255, required=True)
	slug = db.StringField(max_length=255, required=True)
	queues = db.ListField(db.ReferenceField('Queue', reverse_delete_rule=db.PULL))

	def get_absolute_url(self):
		return url_for('room', kwargs={"slug": self.slug})

	def save(self, *args, **kwargs):
		self.slug = UniqueSlugify(uids=[r.slug for r in Room.objects])(self.name)
		super(Room, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.name

	def to_json_dict(self):
		data = self.to_mongo()
		data['_id'] = str(data['_id'])
		data['created_at'] = time.mktime(data['created_at'].timetuple())
		data['queues'] = [ q.to_json_dict() for q in self.queues ]

		return data

	meta = {
		'allow_inheritance': True,
		'indexes': ['slug'],
		'ordering': ['slug']
	}

