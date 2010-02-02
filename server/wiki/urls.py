from django.conf.urls.defaults import *

urlpatterns = patterns('wiki',
    # Example:
    # (r'^server/', include('server.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
    (r'^synckit', 'wiki.synckit'),
    (r'^tokyo', 'wiki.tokyo'),
    (r'^traditional', 'wiki.traditional'),
    (r'^manifest', 'wiki.manifest'),
    (r'^profiling_on', 'wiki.profiling_on'),
    (r'^profiling_off', 'wiki.profiling_off'),
)
