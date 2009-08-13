from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context
from grampsweb.views.models import View
from grampsweb.sortheaders import SortHeaders

def homepage(request):
    """
    Index of all views.
    """
    headers = (('Available Views', 'name'),
               )
    sort_headers = SortHeaders(request, headers, 
                               default_order_field = 0)
    view_list = View.objects.order_by(sort_headers.get_order_by())
    content = {
        'title': 'Homepage - ',
        'heading': 'My Family Tree',
        'footer':  '',
        'copyright': 'Copyright (c) 2009, by Me.',
        'headers' : list(sort_headers.headers()),
        'view_list': view_list,
        #'meta': ,
        }
    context = Context(content)
    return render_to_response('gramps-base.html', context)
                              
def view(request, view, handle=None):
    content = {
        'title': view.title() + ' View - ',
        'heading': view.title() + 'View',
        'footer':  '',
        'copyright': 'Copyright (c) 2009, by Me.',
        #'meta': ,
        }
    context = Context(content)
    return render_to_response('gramps-base.html', context)
    
