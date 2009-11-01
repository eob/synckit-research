from django.http import HttpResponse
from synckit.views import *
from django.template import Context, loader

def main(request):
    t = loader.get_template('runner.html')
    c = Context({})
    return HttpResponse(t.render(c))