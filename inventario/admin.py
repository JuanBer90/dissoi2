from django.contrib import admin
from django.contrib.admin.options import TabularInline
from inventario.models import Categoria, CategoriaDetalle, CategoriaDetalleMovimiento
from ajax_select.admin import AjaxSelectAdmin, AjaxSelectAdminTabularInline
from ajax_select import make_ajax_form

# Register your models here.
class CategoriaDetalleMovimientoAdmin(TabularInline):
    model=CategoriaDetalleMovimiento
    extra=3

class CategoriaDetalleAdmin(admin.ModelAdmin):
    inlines=[CategoriaDetalleMovimientoAdmin,]
    list_filter = ['categoria__nombre']
    
    
class CategoriaDetalleTabInline(AjaxSelectAdminTabularInline):
    model = CategoriaDetalle
    form = make_ajax_form(CategoriaDetalle, {'comunidad': 'comunidad'})
    extra = 3


class CategoriaAdmin(admin.ModelAdmin):
    inlines=[CategoriaDetalleTabInline,]


admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(CategoriaDetalle, CategoriaDetalleAdmin)