from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context
from django.contrib.auth.models import User
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from grampsweb.views.models import View
from grampsweb.grampsdb.models import *
from grampsweb.sortheaders import SortHeaders

def view(request, view, handle=None):
    cview = view.title()
    if view == "event":
        object_list = Event.objects.all()
        headers = ["gramps_id", ]
    elif view == "family":
        object_list = Family.objects.all()
        headers = ["gramps_id",]
    elif view == "media":
        object_list = Media.objects.all()
        headers = ["gramps_id",]
    elif view == "note":
        object_list = Note.objects.all()
        headers = ["gramps_id",]
    elif view == "person":
        object_list = Name.objects.all()
        headers = ["gramps_id", "surname", "first_name"]
    elif view == "place":
        object_list = Place.objects.all()
        headers = ["gramps_id",]
    elif view == "repository":
        object_list = Repository.objects.all()
        headers = ["gramps_id",]
    elif view == "source":
        object_list = Source.objects.all()
        headers = ["gramps_id",]

    paginator = Paginator(object_list, 10) 

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
    context["view"] = cview
    context["headers"] = headers
    return render_to_response('view_page.html', context)
