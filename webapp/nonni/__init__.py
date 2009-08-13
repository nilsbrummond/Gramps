from django.shortcuts import get_object_or_404, render_to_response

from nonni.nonna.models import Person

def home(request, *args, **kwargs):
    content = {
        'title': 'Homepage - ',
        'heading': 'My Family Tree',
        'footer':  'This is the footer!',
        'copyright': 'Copyright (c) 2009, by Me.',
        'person_list': Person.objects.filter(gender=2),
        #'meta': ,
        }
    add_content(content)
    return render_to_response('gramps-base.html', content)
                              

def add_content(data):
    content = {
        'content': 'People with Unknown Gender:',
    }
    return data.update(content)
