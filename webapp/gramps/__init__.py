from django.http import HttpResponse
from gramps.views import index

def homepage(request):
    return index(request)
