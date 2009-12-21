from django.http import HttpResponse
from models import *
from synckit.views import *
from django.template import Context, loader
import json
import time

# This lives outside of a method so it's only instantiated once per
# interpreter instance
manager = ViewManager()
qv = QueueView(Entry, "date", 10)
manager.register("Posts", qv)

query_times = 0.0
template_times = 0.0
num_queries = 0
entries_returned = 0

def report_time(request):
    global query_times
    global template_times
    return HttpResponse("queries=%f,templates=%f,num_queries=%d,entries_returned=%d"%(query_times,template_times,num_queries,entries_returned))

def seepage(request):
    global query_times
    global template_times
    global num_queries
    global entries_returned
    num_queries += 1
    start = time.time()
    results = manager.runqueries(request)
    end = time.time()
    entries_returned += len(results["Posts"]["results"])
    query_times += end-start
    start = time.time()
    response = HttpResponse(json.dumps(results), mimetype='application/json')
    end = time.time()
    template_times += end-start
    return response

def traditional(request):
    # args = generate_view_args(request)[0]
    global query_times
    global template_times
    global num_queries
    global entries_returned
    num_queries += 1
    start = time.time()
    now = request.GET["now"]
    results = list(Entry.objects.all().filter(date__lte = now).order_by('-date')[:10])
    end = time.time()
    query_times += end-start
    entries_returned += len(results)

    start = time.time()
    t = loader.get_template('index.html')
    c = Context({
        'posts': results,
    })
    response = HttpResponse(t.render(c))
    end = time.time()
    template_times += end-start
    return response

def markdone(request):
    return HttpResponse("OK")
