import json

def generate_view_args(request):
    queries = request.REQUEST["queries"]
    views = json.loads(queries)
    return views

class ViewManager:
    def __init__(self):
        self.views = {}
    def register(self, name, view):
        self.views[name] = view
    def runqueries(self, request):
        view_queries = generate_view_args(request)
        results = {}
        for name, query in view_queries.items():
            if name in self.views:
                results[name] = {}
                results[name]["results"] = self.views[name].results(query)
                results[name]["schema"] = self.views[name].schema()
            else:
                results[name] = "no view registered for this query"
        return results

# for more generic stuff, see
# [f.name for f in model_or_instance._meta.fields]
# /usr/share/python-support/python-django/django/db/backends/creation.py
# /usr/share/python-support/python-django/django/core/management/sql.py
class QueueView:
    # order = "ASC" or "DESC"
    def __init__(self, model, sortfield, order="ASC"):
        self.model = model
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
            queryset = self.model.objects.filter(**kwargs)
        else:
            queryset = self.model.objects.all()
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

