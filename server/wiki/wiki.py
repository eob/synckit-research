from django.http import HttpResponse
from models import *
from synckit.views import *
from django.template import Context, loader
import json

# This lives outside of a method so it's only instantiated once per
# interpreter instance
synckit_manager = ViewManager()
synckit_prefetch_config = {"model" : Page,
                   "connected_path" : "inlinks",
                   "probability_field" : "access_probability",
                   "exit_probability" : .5,
                   "size_fields" : ["title", "contents"],
                   "total_time" : .1}
#synckit_sv = SetView(Page, "id", synckit_prefetch_config)
synckit_sv = SetView(Page, "id")
synckit_manager.register("Pages", synckit_sv)

tokyo_manager = ViewManager(ViewManager.SyncType.FLYING_TEMPLATES)
tokyo_sv = SetView(Page, "id")
tokyo_manager.register("Pages", tokyo_sv)

def manifest(request):
    t = loader.get_template('manifest.txt')
    c = Context({})
    return HttpResponse(t.render(c), mimetype="text/cache-manifest")

def synckit(request):
    results = synckit_manager.runqueries(request)
    return HttpResponse(json.dumps(results), mimetype='application/json')

def tokyo(request):
    results = tokyo_manager.runqueries(request)
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
