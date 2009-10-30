from django.conf.urls.defaults import *
import private_settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^server/', include('server.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
    (r'^email/', include('server.emailstubs.urls')),
    (r'^blog/', include('server.blog.urls')),
    (r'^wiki/', include('server.wiki.urls')),
    (r'^performancetest/', include('server.performancetest.urls')),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': private_settings.STATIC_DOC_ROOT}),
)
