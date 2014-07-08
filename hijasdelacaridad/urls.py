try:
    from django.conf.urls import *
except:
    from django.conf.urls.defaults import *
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from ajax_select import urls as ajax_select_urls


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^search_form',  view='asientos_contables.views.search_form', name='search_form'),
    (r'^admin/lookups/', include(ajax_select_urls)),
    (r'^admin/', include(admin.site.urls)),


    #ASIENTOS
    (r'^asiento/nuevo/', 'asientos_contables.views.nuevo'),
    (r'^asiento/listar/', 'asientos_contables.views.listar'),
    (r'^balance/', 'asientos_contables.views.mayores'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
