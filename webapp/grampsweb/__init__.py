from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context
from django.contrib.auth.models import User
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from grampsweb.views.models import View
from grampsweb.grampsdb.models import *
from grampsweb.sortheaders import SortHeaders

def view_detail(request, view, handle):
    cview = view.title()
    context = RequestContext(request)
    context["views"] = View.objects.order_by("name")
    context["cview"] = cview
    context["view"] = view
    context["handle"] = handle
    return render_to_response('view_detail_page.html', context)
    
def view(request, view):
    cview = view.title()
    if view == "event":
        object_list = Event.objects.all().order_by("gramps_id")
        headers = ["gramps_id", ]
    elif view == "family":
        object_list = Family.objects.all().order_by("gramps_id")
        headers = ["gramps_id",]
    elif view == "media":
        object_list = Media.objects.all().order_by("gramps_id")
        headers = ["gramps_id",]
    elif view == "note":
        object_list = Note.objects.all().order_by("gramps_id")
        headers = ["gramps_id",]
    elif view == "person":
        object_list = Name.objects.all().order_by("surname", "first_name")
        headers = ["surname", "first_name"]
    elif view == "place":
        object_list = Place.objects.all().order_by("gramps_id")
        headers = ["gramps_id",]
    elif view == "repository":
        object_list = Repository.objects.all().order_by("gramps_id")
        headers = ["gramps_id",]
    elif view == "source":
        object_list = Source.objects.all().order_by("gramps_id")
        headers = ["gramps_id",]

    paginator = Paginator(object_list, 20) 

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)

    context = RequestContext(request)
    context["page"] = page
    context["views"] = View.objects.order_by("name")
    context["view"] = view
    context["cview"] = cview
    context["headers"] = headers
    return render_to_response('view_page.html', context)
