try:
    from django.conf.urls import *
except:
    from django.conf.urls.defaults import *
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from ajax_select import urls as ajax_select_urls
from dajaxice.core import dajaxice_autodiscover, dajaxice_config

dajaxice_autodiscover()
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^search_form',  view='asientos_contables.views.search_form', name='search_form'),
    (r'^admin/lookups/', include(ajax_select_urls)),
    (r'^admin/', include(admin.site.urls)),
    (dajaxice_config.dajaxice_url, include('dajaxice.urls')),

    #ASIENTOS
    (r'^asiento/nuevo/', 'asientos_contables.views.nuevo'),
    (r'^asiento/listar/', 'asientos_contables.views.listar'),
    (r'^cuentas/mayor/', 'asientos_contables.views.mayores'),
    (r'^mayor/(?P<tipo>.*)', 'asientos_contables.views.mayor'),
    (r'^mayorgeneral/(?P<tipo>.*)', 'asientos_contables.views.mayor_general'),
    (r'^presupuesto/(?P<tipo>.*)', 'presupuestos.views.presupuesto'),
    (r'^presupuesto_comunidad/(?P<tipo>.*)', 'presupuestos.views.presupuesto_comunidad'),
    (r'^ver_presupuesto/', 'presupuestos.views.ver_presupuesto'),
    (r'^ejecucion_presupuestaria/(?P<tipo>.*)', 'presupuestos.views.ejecucion_presupuestaria'),
    (r'^ejecucion_presupuestaria_comunidad/(?P<tipo>.*)', 'presupuestos.views.ejecucion_presupuestaria_comunidad'),
    (r'^balance/comunidad/(?P<id>.*)', 'cuentas.views.balance_comunidad'),
    (r'^balance/consolidado/', 'cuentas.views.balance_general'),
    (r'^balance/pais/(?P<id>.*)', 'cuentas.views.balance_pais'),
    (r'^balance/', 'cuentas.views.ver_balance'),
    (r'^prueba/', 'cuentas.views.prueba'),
    (r'^mayor_detalle_comunidad/(?P<id>\d+)/(?P<tipo>.*)', 'asientos_contables.views.mayor_detallado_comunidad'),
    (r'^mayor_detalle_pais/(?P<id>\d+)/(?P<tipo>.*)', 'asientos_contables.views.mayor_detallado_pais'),
    (r'^mayor_detalle_consolidado/(?P<tipo>.*)', 'asientos_contables.views.mayor_detallado_consolidado'),
    (r'^ver_mayor_detalle/', 'asientos_contables.views.ver_mayor_detalle'),
    (r'^asignar_permiso/(?P<tipo>.*)', 'cuentas.views.asignar_permiso'),
    (r'^cerrar_ejercicio/', 'ejercicios.views.cerrar_ejercicio'),
    (r'^ver_ejercicio/', 'ejercicios.views.ejercicio_actual'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

