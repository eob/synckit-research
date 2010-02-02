from django.conf.urls.defaults import *


urlpatterns = patterns('blog',
    # Example:
    # (r'^server/', include('server.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
    (r'^entries$', 'entries.seepage'),
    (r'^flying_entries$', 'entries.tokyo'),
    (r'^traditional$', 'entries.traditional'),
    (r'^template$', 'entries.template'),
    (r'^markdone$', 'entries.markdone'),
    (r'^report_time$', 'entries.report_time'),
)
