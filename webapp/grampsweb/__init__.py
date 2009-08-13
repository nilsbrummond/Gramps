from django.http import HttpResponse

def homepage(request):
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
