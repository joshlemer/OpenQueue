from flask_restful import Resource
from models import Room
from bson import json_util
import ast

class RoomApi(Resource):
	def get(self, slug):
		#return { 'key' : 'value', 'otherkey': 2}
		#return json.JSONEncoder(Room.objects(slug=slug).first().to_json())
		#return ast.literal_eval(Room.objects(slug=slug).first().to_json())
		room = Room.objects(slug=slug).first()
		if (room):
			return ast.literal_eval(room.to_json())
		return 404

	
	def post(self):
		return "foo post"

