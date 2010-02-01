from django.http import HttpResponse
from synckit.views import *
from django.template import Context, loader
from models import *

def log(request):
    new_one = LogEntry(
        test_batch_name=request.POST["test_batch_name"],
        test_name=request.POST["test_name"],
        test_file=request.POST["test_file"],
        test_style=request.POST["test_style"],
        page_name=request.POST["page_name"],
        url=request.POST["url"],
        params=request.POST["params"],
        user=int(request.POST["user"]),
        visit_number=int(request.POST["visit_number"]),
        total_time_to_render=int(request.POST["total_time_to_render"]),
        latency=float(request.POST["latency"]),
        bandwidth=float(request.POST["bandwidth"]),
        data_fetch=int(request.POST["data_fetch"]),
        data_bulkload=int(request.POST["data_bulkload"]),
        template_parse=int(request.POST["template_parse"])
    )
    new_one.save()
    return HttpResponse('OK')
