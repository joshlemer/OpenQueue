import datetime
from flask import url_for
from qme_src import db

class User(db.Document):
	user_id = db.LongField(min_value=0)
	email = db.EmailField(unique=True)
	password = db.StringField(default=True)
	active = db.BooleanField(default=True)
	isAdmin = db.BooleanField(default=False)
	timestamp = db.DateTimeField(default=datetime.datetime.now())
	def is_active(self):
		return self.active
	def get_id(self):
		return self.user_id
	def is_authenticated(self):
		return True

class Resource(db.Document):
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	name = db.StringField(max_length=255, required=True)
	current_user = db.ReferenceField(User)

class QueueElement(db.EmbeddedDocument):
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	user = db.ReferenceField(User)
	accepts = db.ListField(db.ReferenceField(Resource))

class Queue(db.EmbeddedDocument):
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	name = db.StringField(max_length=255, required=True)
	resources = db.ListField(db.ReferenceField(Resource))
	queue_elements = db.ListField(db.EmbeddedDocumentField('QueueElement'))


class Room(db.Document):
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	name = db.StringField(max_length=255, required=True)
	slug = db.StringField(max_length=255, required=True)
	queues = db.ListField(db.EmbeddedDocumentField('Queue'))

	def get_absolute_url(self):
		return url_for('room', kwargs={"slug": self.slug})

	def __unicode__(self):
		return self.name

	meta = {
		'allow_inheritance': True,
		'indexes': ['slug'],
		'ordering': ['slug']
	}


