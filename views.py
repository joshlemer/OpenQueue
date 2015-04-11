from flask import Blueprint, request, redirect, render_template, url_for
from flask.views import MethodView
from qme_src.models import Room, Resource

rooms = Blueprint('rooms', __name__, template_folder='templates')


class ListView(MethodView):

    def get(self):
        rooms = Room.objects.all()
        return render_template('rooms/list.html', rooms=rooms)


class DetailView(MethodView):

    def get(self, slug):
        room = Room.objects.get_or_404(slug=slug)
        return render_template('rooms/detail.html', room=room)


# Register the urls
rooms.add_url_rule('/', view_func=ListView.as_view('list'))
rooms.add_url_rule('/<slug>/', view_func=DetailView.as_view('detail'))