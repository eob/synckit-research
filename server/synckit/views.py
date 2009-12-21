from django.db.models import Count, Sum, Min, Max

import json
import itertools

__all__ = ["ViewManager", "SetView", "QueueView", "CubeView"]

def generate_view_args(request):
    queries = request.REQUEST["queries"]
    perf = {}
    if "latency" in request.REQUEST:
        perf["latency"] = float(request.REQUEST["latency"])
    if "bandwidth" in request.REQUEST:
        perf["bandwidth"] = float(request.REQUEST["bandwidth"])
    views = json.loads(queries)
    return (views, perf)

class ViewManager:
    def __init__(self):
        self.views = {}
    def register(self, name, view):
        self.views[name] = view
        view.set_name(name)
    def runqueries(self, request):
        (view_queries, perf) = generate_view_args(request)
        results = {}
        for name in view_queries.keys():
            if name in self.views:
                results[name] = {}
                results[name]["results"] = self.views[name].results(view_queries, perf)
            else:
                results[name] = "no view registered for this query"
        return results

class BaseView:
    class ResultFormat:
        """
        Specifies the format in which django will return results.  Django
        usually returns each result as an object with attributes stored in fields.
        Some query types (e.g., ones that include a values() call) will instead
        return a dictionary with attributes as keys.
        """
        (OBJECT_WITH_FIELDS, DICT_WITH_KEYS) = ("OBJECT_WITH_FIELDS", "DICT_WITH_KEYS")

    def __init__(self, model):
        self.model = model
        self.attrs = [f.name for f in model._meta.fields]
        self.parent_view = None
        self.parent_path = None
        self.result_format = BaseView.ResultFormat.OBJECT_WITH_FIELDS
    def results(self, queries, perf):
        results = []
        queryset = self.queryset(queries, perf)
        # TODO: make this a generator rather than instantiating everything
        for result in queryset:
            if self.result_format is BaseView.ResultFormat.OBJECT_WITH_FIELDS:
                results.append([str(getattr(result, field)) for field in self.attrs])
            elif self.result_format is BaseView.ResultFormat.DICT_WITH_KEYS:
                results.append([str(result[field]) for field in self.attrs])
            else:
                raise TypeError("Invalid result format: %s" % (self.result_format))
        return results
    def queryset(self, queries, perf):
        queryset = self.queryset_impl(queries[self.view_name], perf)
        queryset = self.limit_to_parent(queryset, queries, perf)
        return queryset
    def queryset_impl(self, query, perf):
        raise  NotImplementedError()
    def limit_to_parent(self, queryset, queries, perf):
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
    def __init__(self, model, idfield, prefetch_config=None):
        BaseView.__init__(self, model)
        self.idfield = idfield
        self.idin = "%s__in" % (self.idfield)
        self.prefetcher = None
        if not prefetch_config == None:
            self.prefetcher = Prefetcher(prefetch_config)

    def queryset_impl(self, query, perf):
        queryset = self.model.objects
        
        exclude = []
        if "exclude" in query:
            exclude = query["exclude"]
            kwargs = {self.idin : exclude}
            queryset = queryset.exclude(**kwargs)
        if "filter" in query:
            kwargs = {self.idin : query["filter"]}
            queryset = self.model.objects.filter(**kwargs)
        
        if (not self.prefetcher == None) and (queryset.count() == 1):
            prefetch_query = self.prefetcher.fetch(queryset[0], exclude, perf)
            # unioning only works if objects are of the same type
            queryset = itertools.chain(queryset, prefetch_query)

        return queryset

# prefetch_config is a dictionary with the following fields:
#   model (django model)---the related model object to retrieve
#   connected_path (string)---the path from the related object to the set's
#       model object
#   probability_field (string)---the field on the related object containing
#       its probability
#   exit_probability (float)---the likelihood of leaving any page
#   size_fields (list of strings)---the list of fields on the related
#       object which should go into calculating its size.
#   total_time---the time the client is willing to block 
class Prefetcher():
    def __init__(self, config):
        self.config = config
        # generate "length(field1)+...+length(fieldN)" for the number of size
        # fields.
        length_fields = ["length(%s)" % (field) for field in self.config["size_fields"]]
        length_str = "+".join(length_fields)
        self.select_addition = { "object_size" : length_str}
        self.onlyfields = ["id", self.config["probability_field"]]
    # object is the model object you are sending back.
    # already_have is a list of object ids the client already has.
    def fetch(self, object, already_have, perf):
        kwargs = {self.config["connected_path"] : object}
        queryset = self.config["model"].objects.filter(**kwargs)
#        kwargs = {"id__in" : already_have}
#        queryset = queryset.exclude(**kwargs)
        queryset = queryset.only(*self.onlyfields)
        queryset = queryset.extra(select = self.select_addition)
        ids = self.pick_objects(object, already_have, queryset, perf)
        return self.config["model"].objects.filter(id__in = ids)
   
    def pick_objects(self, object, already_have, queryset, perf):
        items = self.normalize_probabilities(queryset, already_have)
        for item in items:
            item.benefit = perf["latency"]
            cost = self.calculate_cost(item.object_size, perf)
            cost = cost*(1-getattr(item, self.config["probability_field"]))
            item.benefit -= cost
        items.sort(benefit_compare)
        return self.additional_items(object, items, perf)
 
    def calculate_cost(self, object_size, perf):
        cost = perf["latency"]
        cost += (object_size / perf["bandwidth"])
        return cost

    def normalize_probabilities(self, queryset, already_have):
        sum = 0.0
        for item in queryset:
            sum += getattr(item, self.config["probability_field"])
        items = []
        denominator = sum/(1-self.config["exit_probability"])
        already_have = set(already_have)
        for item in queryset:
            if item.id not in already_have:
                newprob = getattr(item, self.config["probability_field"])
                setattr(item, self.config["probability_field"], newprob/denominator)
                items.append(item)
        return items
     
    def additional_items(self, object, items, perf):
        size = self.calculate_size(object)
        time = self.calculate_cost(size, perf)
        ids = []
        for item in items:
            more_time = item.object_size / perf["bandwidth"]
            if (item.benefit > 0) and (time + more_time < self.config["total_time"]):
                ids.append(item.id)
                time += more_time
            else:
                break
        return ids
 
    def calculate_size(self, object):
        size = 0
        for field in self.config["size_fields"]:
            size += len(getattr(object, field))
        return size

def benefit_compare(x,y):
    if x.benefit > y.benefit:
        return -1
    elif x.benefit == y.benefit:
        return 0
    else:
        return 1

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
    def queryset_impl(self, query, perf):
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

class CubeView(BaseView):
    """
    Aggregates model objects grouped by cube_fields.  Returns the 
    aggregate_type function over the aggregate_field for each cube_field grouping.
    Similar to:

    SELECT cube_fields, aggregate_type(aggregate_field) AS aggregate
    FROM model
    GROUP BY cube_fields;
    """
    
    class AggType:
        """
        Aggregates we handle
        """
        (COUNT, SUM, MIN, MAX) = ("COUNT", "SUM", "MIN", "MAX")
    
    AGGREGATE = "aggregate"
    
    def __init__(self, model, cube_fields, aggregate_type, aggregate_field = "id"):
        BaseView.__init__(self, model)
        # We're not returning an array of model objects.  We're instead
        # returning a set of aggregate values grouped by cube_fields.  As
        # such, the attributes will be the cube_fields and the aggregate
        # value.
        self.attrs = list(cube_fields)
        self.attrs.append(CubeView.AGGREGATE)
        self.cube_fields = cube_fields
        self.aggregate_args = { CubeView.AGGREGATE: \
                                self.build_agg(aggregate_type, aggregate_field) }
        # django will return results as a dictionary because we call values()
        # in the queryset
        self.result_format = BaseView.ResultFormat.DICT_WITH_KEYS
    def queryset_impl(self, query, perf):
        """
        Returns the aggregate over the grouped fields.  Eventually, we'll have
        query include the last time the aggregate was requested by the client,
        and only send updated fields.  Additionally, we'll potentially look
        at perf to determine how large a datacube the client can handle.
        """
        # Include GROUP BY
        queryset = self.model.objects.values(*self.cube_fields)
        # Remove any default orderings of the ORM
        queryset = queryset.order_by()
        # Include aggregate
        queryset = queryset.annotate(**self.aggregate_args)
        return queryset

    def build_agg(self, aggregate_type, aggregate_field):
        if aggregate_type is CubeView.AggType.COUNT:
            return Count(aggregate_field)
        elif aggregate_type is CubeView.AggType.SUM:
            return Sum(aggregate_field)
        elif aggregate_type is CubeView.AggType.MIN:
            return Min(aggregate_field)
        elif aggregate_type is CubeView.AggType.MAX:
            return Max(aggregate_field)
        else:
            raise TypeError("Invalid aggregate type: %s" % (aggregate_type))
