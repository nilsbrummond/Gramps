from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^gramps/', include('gramps.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)

# View URLs:

urlpatterns += patterns('',
    (r'^$', 'gramps.homepage'),
    (r'^view/$', 'gramps.views.index'),
    (r'^view/(?P<view>(.*))/$', 'gramps.views.dispatch'),
    (r'^view/(?P<view>(.*))/(?P<handle>(.*))$', 'gramps.views.dispatch'),
)

# Add other URLs here:
