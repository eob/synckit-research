from django.http import HttpResponse
from models import *
import datetime
import json
import re

class MessageEndpoint:
    def results(self, client_params):
        queryset = Message.objects.filter(date__gt = client_params["max"])
        messages = []
        # TODO: HACK HACK HACK---make this return a generator---no sense in
        # wasting memory on the responses
        for message in queryset:
            messages.append([message.id, message.from_email, message.to_email, \
                             message.subject, message.contents, str(message.date)])
        return messages
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
    manager.register("Messages", MessageEndpoint())
    results = manager.runqueries(endpoints)
    return HttpResponse(json.dumps(results), mimetype='application/json')

def generate_endpoint_args(request):
    queries = request.REQUEST["queries"]
    endpoints = json.loads(queries)
    return endpoints
