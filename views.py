from flask import Blueprint, request, redirect, render_template, url_for
from flask.views import MethodView
from flask.ext.mongoengine.wtf import model_form
from qme_src.models import Room, Resource

rooms = Blueprint('rooms', __name__, template_folder='templates')


class ListView(MethodView):

    def get(self):
        rooms = Room.objects.all()
        return render_template('rooms/list.html', rooms=rooms)


class DetailView(MethodView):

    form = model_form(Resource, exclude=['created_at'])

    def get_context(self, slug):
        room = Room.objects.get_or_404(slug=slug)
        form = self.form(request.form) 

        context = {
        	'room': room,
        	'form': form
        }
        return context



    def get(self, slug):
        context = self.get_context(slug)
        return render_template('rooms/detail.html', **context)

    def post(self, slug):
        context = self.get_context(slug)
        form = context.get('form')

        if form.validate():
            resource = Resource()
            form.populate_obj(resource)

            resource = context.get('resource')
            room.resources.append(resource)
            room.save()

            return redirect(url_for('rooms.detail', slug=slug))

        return render_template('rooms/detail.html', **context)

class QueueAPI(MethodView):

	def join_queue():
		pass

# Register the urls
rooms.add_url_rule('/', view_func=ListView.as_view('list'))
rooms.add_url_rule('/rooms/<slug>/', view_func=DetailView.as_view('detail'))