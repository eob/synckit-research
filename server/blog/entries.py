from django.http import HttpResponse
from models import *
from synckit.views import *
from django.template import Context, loader

# This lives outside of a method so it's only instantiated once per
# interpreter instance
manager = ViewManager()
qv = QueueView(Entry, "date", 10)
manager.register("Posts", qv)

def seepage(request):
    results = manager.runqueries(request)
    return HttpResponse(json.dumps(results), mimetype='application/json')

def traditional(request):
    args = generate_view_args(request)
    now = args["Posts"]["now"]
    results = Entry.objects.all().filter(date__lte = now).order_by('-date')[:10]

    t = loader.get_template('index.html')
    c = Context({
        'posts': results,
    })
    return HttpResponse(t.render(c))

def template(request):
    t = loader.get_template('index_template.html')
    c = Context({})
    return HttpResponse(t.render(c))
