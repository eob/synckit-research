from django.http import HttpResponse
from models import *
from synckit.views import *

# This lives outside of a method so it's only instantiate  once per
# interpreter instance
manager = ViewManager()
manager.register("Messages", QueueView(Message, "date"))
# manager.register("Tags", 
# SetView(Tag, "id", "Messages m", "m.to = ME.id AND tag.mid = m.id"))
#                     $1            $2
#             SqlView
# SELECT __ FROM Tags t $1 WHERE ___ AND ($2)

def inbox(request):
    results = manager.runqueries(request)
    return HttpResponse(json.dumps(results), mimetype='application/json')
