from django.http import HttpResponse
from models import *
from synckit.views import *

# This lives outside of a method so it's only instantiated once per
# interpreter instance
manager = ViewManager()
manager.register("Messages", QueueView(Message, "date"))

def inbox(request):
    results = manager.runqueries(request)
    return HttpResponse(json.dumps(results), mimetype='application/json')
