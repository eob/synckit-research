from django.http import HttpResponse
from models import *
from synckit.views import *

# This lives outside of a method so it's only instantiated once per
# interpreter instance
manager = ViewManager()
qv = QueueView(Message, "date")
sv = SetView(Tag, "id")
sv.set_parent(qv, "message")
manager.register("Messages", qv)
manager.register("Tags", sv)

def inbox(request):
    results = manager.runqueries(request)
    return HttpResponse(json.dumps(results), mimetype='application/json')
