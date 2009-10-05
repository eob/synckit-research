from django.http import HttpResponse
from models import *
import datetime
import json
import re

# for more generic stuff, see
# [f.name for f in model_or_instance._meta.fields]
# /usr/share/python-support/python-django/django/db/backends/creation.py
# /usr/share/python-support/python-django/django/core/management/sql.py

class QueueEndpoint:
    # order = "ASC" or "DESC"
    def __init__(self, model, sortfield, order="ASC"):
        self.attrs = [f.name for f in model._meta.fields]
        self.order = order
        self.sortfield = sortfield
    def results(self, client_params):
        queryset = None
        minmax = "max" if self.order == "ASC" else "min"
        if minmax in client_params:
            gtlt = "gt" if self.order == "ASC" else "lt"
            fieldcompare = "%s__%s" % (self.sortfield, gtlt)
            kwargs = {fieldcompare: client_params[minmax]}
            queryset = Message.objects.filter(**kwargs)
        else:
            queryset = Message.objects.all()
        posneg = "" if self.order == "ASC" else "-"
        queryset = queryset.order_by("%sdate" % (posneg))

        results = []
        for result in queryset:
            results.append([str(getattr(result, field)) for field in self.attrs])
        return results
    def schema(self):
        return ["id integer NOT NULL PRIMARY KEY", \
                "from_email varchar(200) NOT NULL", \
                "to_email varchar(200) NOT NULL", \
                "subject varchar(200) NOT NULL", \
                "contents text NOT NULL", \
                "date datetime NOT NULL"] \

class EndpointManager:
    def __init__(self):
        self.endpoints = {}
    def register(self, name, endpoint):
        self.endpoints[name] = endpoint
    def runqueries(self, endpoint_queries):
        results = {}
        for name, query in endpoint_queries.items():
            if name in self.endpoints:
                results[name] = {}
                results[name]["results"] = self.endpoints[name].results(query)
                results[name]["schema"] = self.endpoints[name].schema()
            else:
                results[name] = "no endpoint registered for this query"
        return results

def contents(request):
    return generate_response(Message.objects.all())

def inbox(request):
    endpoints = generate_endpoint_args(request)
    manager = EndpointManager()
    manager.register("Messages", QueueEndpoint(Message, "date"))
    results = manager.runqueries(endpoints)
    return HttpResponse(json.dumps(results), mimetype='application/json')

def generate_endpoint_args(request):
    queries = request.REQUEST["queries"]
    endpoints = json.loads(queries)
    return endpoints
