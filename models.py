import datetime, time
from flask import url_for
from __init__ import db, bcrypt
from bson import json_util
import ast

class User(db.Document):
	user_id = db.LongField(min_value=0)
	email = db.EmailField(unique=True)
	password = db.StringField(default=True)
	active = db.BooleanField(default=True)
	isAdmin = db.BooleanField(default=False)
	timestamp = db.DateTimeField(default=datetime.datetime.now())

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

class QueueElement(db.EmbeddedDocument):

	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	user = db.ReferenceField(User)
	accepts = db.ListField(db.ReferenceField('Resource'))

	def to_json_dict(self, follow_refs=True):
		data = self.to_mongo()
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
	current_queue_element = db.EmbeddedDocumentField('QueueElement')

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

class Queue(db.EmbeddedDocument):
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	name = db.StringField(max_length=255, required=True)
	resources = db.ListField(db.ReferenceField(Resource))
	queue_elements = db.ListField(db.EmbeddedDocumentField('QueueElement'))

	def to_json_dict(self):
		data = self.to_mongo()
		data['created_at'] = time.mktime(data['created_at'].timetuple())
		data['resources'] = [ r.to_json_dict() for r in self.resources ]
		data['queue_elements'] = [ qe.to_json_dict() for qe in self.queue_elements ]

		return data

	def add_queue_element(self, queue_element):
		self.queue_elements.append(queue_element)
		self.flush_queue()

	def flush_queue(self):
		for queue_element in self.queue_elements:
			for resource in queue_element.accepts:
				if resource.current_queue_element is None:
					resource.current_queue_element = queue_element
					self.queue_elements.remove(queue_element)
					resource.save()


class Room(db.Document):
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	name = db.StringField(max_length=255, required=True)
	slug = db.StringField(max_length=255, required=True)
	queues = db.ListField(db.EmbeddedDocumentField('Queue'))

	def get_absolute_url(self):
		return url_for('room', kwargs={"slug": self.slug})

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

