from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

from grampsweb.grampsdb.views import *

urlpatterns = patterns('',
    # Specific matches first:
    (r'^admin/(.*)', admin.site.root),
)

urlpatterns += patterns('',
    # DANGEROUS in production:
     (r'^styles/(?P<path>.*)$', 'django.views.static.serve',
      {'document_root': 
          '/home/dblank/gramps/gep-013-server/webapp/html/styles', 
       'show_indexes': 
          True},
      ),
     (r'^images/(?P<path>.*)$', 'django.views.static.serve',
      {'document_root': 
          '/home/dblank/gramps/gep-013-server/webapp/html/images', 
       'show_indexes': 
          True},
      ),
)

# The rest will match views:
urlpatterns += patterns('',
    (r'^$', main_page),
    (r'^user/(\w+)/$', user_page),
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', logout_page),
    (r'^(?P<view>(\w+))/$', 'grampsweb.view'),
    (r'^(?P<view>(\w+))/(?P<handle>(\w+))/$', 'grampsweb.view_detail'),
)
