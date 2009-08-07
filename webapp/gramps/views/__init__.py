from django.http import HttpResponse
from gramps.views.models import View
from gramps.views.views import detail, page, get_cursor
from gramps.databases import gapi

def index(request):
    """
    Index of all views.
    """
    view_list = View.objects.all().order_by('name')
    output = "<h1>%s</h1>" % "GRAMPS"
    output += "<b>%s</b>: %s <br />" % ("Family tree", 
                                        gapi.dbstate.db.summary["Family tree"])
    output += "<hr>"
    for view in view_list:
        output += ('<li><a href=\"/view/%s\">%s</a> (%d)</li>' %
                   (view.name.lower(), 
                    view.name, 
                    len(get_cursor(view.name.lower()))))
    output += "<hr>"
    output += "<p>[<a href=\"/admin/\">Admin</a>]</p>"
    return HttpResponse(output)

def dispatch(request, view=None, handle=None):
    """
    Dispatch page view to either detail or page.
    """
    if view and handle:
        return detail(request, view, handle)
    elif view:
        return page(request, view)
    return HttpResponse("Error")

