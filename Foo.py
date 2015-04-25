from flask_restful import Resource
from flask import abort
from models import Room
from bson import json_util
import ast

class RoomApi(Resource):
	def get(self, slug):
		room = Room.objects(slug=slug).first()
		if (room):
			return ast.literal_eval(room.to_json())
		abort(404)
		
	def post(self):
		return "foo post"

