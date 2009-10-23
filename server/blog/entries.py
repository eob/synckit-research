from django.http import HttpResponse
from models import *
from synckit.views import *

# This lives outside of a method so it's only instantiated once per
# interpreter instance
manager = ViewManager()
qv = QueueView(Entry, "date", 10)
manager.register("Posts", qv)

def seepage(request):
    results = manager.runqueries(request)
    return HttpResponse(json.dumps(results), mimetype='application/json')
