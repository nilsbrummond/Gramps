from django.http import HttpResponse
from gramps.views.models import View
from gramps.databases import gapi, get_summary
from gen.db import CLASS_TO_OBJ_MAP

def page(request, view):
    start = int(request.GET.get("start", "0"))
    stop = start + 15
    output = "<h1>GRAMPS %s View</h1>" % view.title()
    output += "<p>%d entries</p>" % len(get_cursor(view))
    output += "[<a href=\"/\">Home</a>] "
    output += "<hr>"
    with get_cursor(view) as cursor:
        count = 0
        for handle, data in cursor:
            count += 1
            if count > stop:
                break
            if count < start:
                continue
            obj = get_object(view, data=data)
            output += "%d. <a href=\"%s\">%s</a><br />" % \
                (count, handle, gapi.sdb.format(obj))
    output += "<hr>"
    output += "[<a href=\"?start=%s\">first</a>] " % 0
    output += "[<a href=\"?start=%s\">prev</a>] " % (start - 15)
    output += "[<a href=\"?start=%s\">next</a>] " % (start + 15)
    output += "[<a href=\"?start=%s\">last</a>] " % (gapi.dbstate.db.total - 15)
    return HttpResponse(output)

def detail(request, view, handle):
    output = "<h1>%s View</h1>" % view.title()
    data = gapi.sdb.details(get_object(view, handle=handle))
    for key in data:
        if key == "Father":
            field = "<a href=\"/view/person/%s\">%s</a>" % (data["Father handle"], data[key])
        elif key == "Mother":
            field = "<a href=\"/view/person/%s\">%s</a>" % (data["Mother handle"], data[key])
        elif "handle" in key:
            continue
        else:
            field = data[key]
        output += "<b>%s</b>: %s<br />" % (key, field)
    return HttpResponse(output)

def get_cursor(view):
    cursor = gapi.dbstate.db.__getattribute__("get_%s_cursor" % view)
    return cursor()

def get_object(view, handle=None, data=None):
    view = view.title()
    if data:
        constr_name = View.objects.all().filter(name=view)[0].constructor
        obj = CLASS_TO_OBJ_MAP[constr_name]()
        obj.unserialize(data) 
        return obj
    elif handle:
        if view == 'Person':
            return gapi.dbstate.db.get_person_from_handle(handle)
        elif view == 'Family':
            return gapi.dbstate.db.get_family_from_handle(handle)
        else:
            raise AttributeError("TODO: %s" % view)
    else:
        raise AttributeError("can't get_object")
