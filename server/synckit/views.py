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
    def set_parent(self, parent_view, parent_path):
        self.parent_view = parent_view
        self.parent_path = parent_path
    def set_name(self, view_name):
        self.view_name = view_name

class SetView(BaseView):
    def __init__(self, model, idfield):
        BaseView.__init__(self, model)
        self.idfield = idfield
        self.idin = "%s__in" % (self.idfield)
    def queryset_impl(self, query):
        queryset = none
        if "exclude" in query:
            kwargs = {self.idin : query["exclude"]}
            queryset = self.model.objects.exclude(**kwargs)
        elif "filter" in query:
            kwargs = {self.idin : query["filter"]}
            queryset = self.model.objects.filter(**kwargs)
        else:
            queryset = self.model.objects.all()

        return queryset 

# for more generic stuff, see
# [f.name for f in model_or_instance._meta.fields]
# /usr/share/python-support/python-django/django/db/backends/creation.py
# /usr/share/python-support/python-django/django/core/management/sql.py
class QueueView(BaseView):
    # order = "ASC" or "DESC"
    def __init__(self, model, sortfield, limit, order="ASC"):
        BaseView.__init__(self, model)
        self.order = order
        self.sortfield = sortfield
        self.limit = limit
        # if our queue increases in the ascending direction, order the
        # results in descending order to get the top ones.
        self.orderby = "-%s" % (sortfield) if order == "ASC" else sortfield
        # if we're increasing in ascending direction, the client will send
        # us the max
        self.minmax = "max" if order == "ASC" else "min"
        # if we're increasing in ascending direction, we want things
        # greater than the max
        self.gtlt = "gt" if order == "ASC" else "lt"
        self.fieldcompare = "%s__%s" % (self.sortfield, self.gtlt)
    def queryset_impl(self, query):
        queryset = None
        kwargs = {}
        if self.minmax in query:
            kwargs[self.fieldcompare] = query[self.minmax]
        if "now" in query:
            kwargs["date__lte"] = query["now"]
        queryset = self.model.objects.filter(**kwargs)
        queryset = queryset.order_by(self.orderby)
        queryset = queryset[:self.limit]
 
        return queryset
