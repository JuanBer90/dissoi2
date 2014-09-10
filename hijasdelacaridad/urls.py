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
    
    (r'^admin/jsi18n', 'django.views.i18n.javascript_catalog'),
    url(r'^search_form',  view='asientos_contables.views.search_form', name='search_form'),
    (r'^admin/lookups/', include(ajax_select_urls)),
    (r'^admin/', include(admin.site.urls)),
    (dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    #BANCOS
    (r'^cuentas_bancarias/(?P<id_comunidad>\d+)/(?P<id_banco>\d*)$', 'cuentas_bancarias.views.cuentas_bancarias'),
    (r'^cuentas_bancarias/comunidad/$', 'cuentas_bancarias.views.sel_comunidad_cuenta_bancaria'),    
    #REPORTES
    (r'^set_ejercicio/$', 'ejercicios.views.set_ejercicio'),
    (r'^reporte/$', 'asientos_contables.reports.some_view'),
    (r'^reporte_cuentas_bancarias_comunidad/(?P<id_comunidad>\d+)/$', 'asientos_contables.reports.cuentas_bancarias_comunidad'),
    (r'^reporte_inventario_general/$', 'asientos_contables.reports.inventario_general'),
    (r'^reporte_inventario/(?P<id_comunidad>\d+)/$', 'asientos_contables.reports.inventario_comunidad'),
    (r'^reporte_mayor/(?P<id_comunidad>\d+)/(?P<desde>[\w\-.]+)/(?P<hasta>[\w\-.]+)/$', 'asientos_contables.reports.mayor'),
    (r'^reporte_mayor_detalle/(?P<id_comunidad>\d+)/(?P<desde>[\w\-.]+)/(?P<hasta>[\w\-.]+)/$', 'asientos_contables.reports.mayor_detalle'),
    (r'^reporte/comunidad/(?P<id_comunidad>\d+)/$', 'asientos_contables.views.sel_comunidad_reporte_mayor'),
    (r'^reporte/comunidad/(?P<id_comunidad>\d+)/(?P<tipo>.*)$', 'asientos_contables.views.sel_comunidad_reporte_mayor'),
    
    #INVENTARIOS
    (r'^inventario/general/$', 'inventario.views.inventario_general'),
    (r'^inventario/comunidad/$', 'inventario.views.seleccionar_comunidad'),
    (r'^inventario/categoria/(?P<id_comunidad>\d*)$', 'inventario.views.inventario_comunidad'),
    (r'^inventario/categoria/(?P<id_comunidad>\d+)/(?P<id>\d+)$', 'inventario.views.inventario_comunidad'),
    (r'^inventario/categoria_detalle/(?P<id_comunidad>\d+)/(?P<id_categoria>\d+)$', 'inventario.views.categoria_detalle'),
    (r'^inventario/categoria_detalle/(?P<id_comunidad>\d+)/(?P<id_categoria>\d+)/(?P<id>\d+)$', 'inventario.views.categoria_detalle'),
    (r'^inventario/movimiento/(?P<id_detalle>\d+)/(?P<id>\d+)$', 'inventario.views.movimiento'),
    (r'^inventario/movimiento/(?P<id_detalle>\d+)$', 'inventario.views.movimiento'),
    (r'^inventario/movimiento_list/(?P<id_detalle>\d+)$', 'inventario.views.movimiento_list'),
    #ASIENTOS
    (r'^asiento/comunidad/$', 'asientos_contables.views.sel_comunidad_asiento'),
    (r'^asiento/nuevo/$', 'asientos_contables.views.nuevo'),
    (r'^asiento/nuevo/(?P<id_comunidad>\d+)/$', 'asientos_contables.views.nuevo'),
    (r'^asiento/editar/(?P<id>\d+)/$', 'asientos_contables.views.editar'),
    (r'^asiento/listar/', 'asientos_contables.views.listar'),
    (r'^cuentas/mayor/', 'asientos_contables.views.mayores'),
    (r'^mayor/(?P<tipo>.*)', 'asientos_contables.views.mayor'),
    (r'^mayorgeneral/(?P<tipo>.*)', 'asientos_contables.views.mayor_general'),
    
    #PRESUPUESTOS
    (r'^presupuesto_comunidad/(?P<id>\d+)/(?P<tipo>\w+)', 'presupuestos.views.presupuesto_comunidad'),
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
    
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

