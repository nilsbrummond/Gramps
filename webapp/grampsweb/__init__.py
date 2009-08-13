from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context
from grampsweb.views.models import View

def homepage(request, *args, **kwargs):
    """
    Index of all views.
    """
    view_list = View.objects.all().order_by('name')
    content = {
        'title': 'Homepage - ',
        'heading': 'My Family Tree',
        'footer':  'This is the footer!',
        'copyright': 'Copyright (c) 2009, by Me.',
        'view_list': view_list,
        'person_list': [], #Person.objects.filter(gender=2),
        #'meta': ,
        }
    context = Context(content)
    return render_to_response('gramps-base.html', context)
                              
