from django.http import HttpResponse
from synckit.views import *
from django.template import Context, loader
from models import *

def log(request):
    new_one = LogEntry(
        tester=request.POST["tester"],
        tester_comments=request.POST["tester_comments"],
        test_file=request.POST["test_file"],
        test_description=request.POST["test_description"],
        style=request.POST["style"],
        url=request.POST["url"],
        params=request.POST["params"],
        user=int(request.POST["user"]),
        visit_number=int(request.POST["visit_number"]),
        total_time_to_render=int(request.POST["total_time_to_render"]),
        latency=int(request.POST["latency"]),
        bandwidth=int(request.POST["bandwidth"]),
        data_fetch=int(request.POST["data_fetch"]),
        data_bulkload=int(request.POST["data_bulkload"]),
        template_parse=int(request.POST["template_parse"])
    )
    new_one.save()
    return HttpResponse('OK')
