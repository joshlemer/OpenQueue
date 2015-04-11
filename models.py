import datetime
from flask import url_for
from qme_src import db

#class User(db.Document):

class Resource(db.EmbeddedDocument):
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	name = db.StringField(max_length=255, required=True)

class Room(db.Document):
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	name = db.StringField(max_length=255, required=True)
	slug = db.StringField(max_length=255, required=True)
	resources = db.ListField(db.EmbeddedDocumentField('Resource'))

	def get_absolute_url(self):
		return url_for('room', kwargs={"slug": self.slug})

	def __unicode__(self):
		return self.name

	meta = {
		'allow_inheritance': True,
		'indexes': ['slug'],
		'ordering': ['slug']
	}

