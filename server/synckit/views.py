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
        view.set_name(name)
    def runqueries(self, request):
        view_queries = generate_view_args(request)
        results = {}
        for name in view_queries.keys():
            if name in self.views:
                results[name] = {}
                results[name]["results"] = self.views[name].results(view_queries)
                results[name]["schema"] = self.views[name].schema()
            else:
                results[name] = "no view registered for this query"
        return results

class BaseView:
    def __init__(self, model):
        self.model = model
        self.attrs = [f.name for f in model._meta.fields]
        self.parent_view = None
        self.parent_path = None
    def results(self, queries):
        results = []
        queryset = self.queryset(queries)
        # TODO: make this a generator rather than instantiating everything
        for result in queryset:
            results.append([str(getattr(result, field)) for field in self.attrs])
        return results
    def queryset(self, queries):
        queryset = self.queryset_impl(queries[self.view_name])
        queryset = self.limit_to_parent(queryset, queries)
        return queryset
    def queryset_impl(self, query):
        raise  NotImplementedError()
    def limit_to_parent(self, queryset, queries):
        if self.parent_view:
            kwargs = {"%s__in" % (self.parent_path) :
                      self.parent_view.queryset(queries)}
            queryset = queryset.filter(**kwargs)
        return queryset
    def schema(self):
        raise  NotImplementedError()
    def set_parent(self, parent_view, parent_path):
        self.parent_view = parent_view
        self.parent_path = parent_path
    def set_name(self, view_name):
        self.view_name = view_name

class SetView(BaseView):
    def __init__(self, model, idfield):
        BaseView.__init__(self, model)
        self.idfield = idfield
    def queryset_impl(self, query):
        ids = None
        if "items" in query:
            ids = query["items"]
        else:
            ids = []
        queryset = self.model.objects.exclude(id__in = ids)
        return queryset 
    def schema(self):
        pass

# for more generic stuff, see
# [f.name for f in model_or_instance._meta.fields]
# /usr/share/python-support/python-django/django/db/backends/creation.py
# /usr/share/python-support/python-django/django/core/management/sql.py
class QueueView(BaseView):
    # order = "ASC" or "DESC"
    def __init__(self, model, sortfield, order="ASC"):
        BaseView.__init__(self, model)
        self.order = order
        self.sortfield = sortfield
    def queryset_impl(self, query):
        queryset = None
        minmax = "max" if self.order == "ASC" else "min"
        if minmax in query:
            gtlt = "gt" if self.order == "ASC" else "lt"
            fieldcompare = "%s__%s" % (self.sortfield, gtlt)
            kwargs = {fieldcompare: query[minmax]}
            queryset = self.model.objects.filter(**kwargs)
        else:
            queryset = self.model.objects.all()
        
        return queryset
    def schema(self):
        return ["id integer NOT NULL PRIMARY KEY", \
                "from_email varchar(200) NOT NULL", \
                "to_email varchar(200) NOT NULL", \
                "subject varchar(200) NOT NULL", \
                "contents text NOT NULL", \
                "date datetime NOT NULL"] \
