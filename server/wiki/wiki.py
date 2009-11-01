from django.http import HttpResponse
from models import *
from synckit.views import *
from django.template import Context, loader

# This lives outside of a method so it's only instantiated once per
# interpreter instance
manager = ViewManager()
prefetch_config = {"model" : Page,
                   "connected_path" : "inlinks",
                   "probability_field" : "access_probability",
                   "exit_probability" : .5,
                   "size_fields" : ["title", "contents"],
                   "total_time" : .25}
sv = SetView(Page, "id", prefetch_config)
manager.register("Pages", sv)

def seepage(request):
    results = manager.runqueries(request)
    return HttpResponse(json.dumps(results), mimetype='application/json')

def traditional(request):
    pageid = request.GET.get('pageid')
    results = Page.objects.all().filter(id = int(pageid))

    t = loader.get_template('wikipage.html')
    c = Context({
        'pages': results,
    })
    return HttpResponse(t.render(c))

def markdone(request):
    return HttpResponse("OK")
