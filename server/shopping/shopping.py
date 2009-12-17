from django.http import HttpResponse
from models import *
from synckit.views import *
from django.template import Context, loader
import json

# This lives outside of a method so it's only instantiated once per
# interpreter instance
#  - cv = CubeView(DesktopPC, ["price", "manufacturer", "usage", "cpu", "hdd"], CubeView.COUNT)
#  - allow arbitrary filters AND join predicates
#  - client gets back table with
#    "price", "manufacturer", "usage", "cpu", "hdd", COUNT
#     $20     HP              home     intel  10     3
#     $30     HP              home     intel  10     3
#     $30     HP              office   intel  10     4
#    server stores date on each of those tuples, so when things get updated,
#      client only gets records newer than lastdownload date
#      question: is this just a closed set that's being shipped with a
#      queueview to result in updates?
#    rather than query="SELECT * FROM ...", we allow
#    SELECT usage, SUM(count) FROM summary WHERE manufacturer = "HP" 
#    GROUP BY Manufacturer
#    GROUP BY SET (Manufacturer, 
#    query="ALL, 'Hewlett-Packard', ALL, ALL, ALL" and gets back a count
#      <$
#    
#    question: what would a declarative query language can we think of that would
#    build faceted navigation interfaces/the data to build them?
#
#    issue: price is a range.  how do we allow binning in the group by?

manager = ViewManager()
cv = CubeView(DesktopPC, ["price", "manufacturer__name", "usage__description", "cpu__model", "hdd__model"], CubeView.AggType.COUNT)
manager.register("pcs", cv)

def pc_cube(request):
    results = manager.runqueries(request)
    return HttpResponse(json.dumps(results), mimetype='application/json')

def markdone(request):
    return HttpResponse("OK")
