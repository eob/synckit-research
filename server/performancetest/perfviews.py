from django.http import HttpResponse

ret_strings = {}

def bytes(request):
    num_bytes = int(request.REQUEST['num_bytes'])
    if num_bytes not in ret_strings:
        ret_strings[num_bytes] = 'a'*num_bytes
    return HttpResponse(ret_strings[num_bytes])
