# Create your views here.

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.template import RequestContext
from grampsweb.views.models import View

def main_page(request):
    context = RequestContext(request)
    context["views"] = View.objects.order_by("name")
    return render_to_response("main_page.html", context)
                              
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

def user_page(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404('Requested user not found.')
    context = RequestContext(request)
    context["username"] =  username
    context["views"] = View.objects.order_by("name")
    return render_to_response('user_page.html', context)
