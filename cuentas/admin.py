from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from cuentas.models import Cuenta

class CuentaAdmin(TreeAdmin):
    form = movenodeform_factory(Cuenta)
    list_display = ('codigo', 'cuenta')
    list_filter = ['tipo']
    def save_model(self, request, cuenta, form, change):
        cuenta.codigo_ordenado = cuenta.codigo_conversion()
        print cuenta.codigo_conversion()
        cuenta.save()
        
admin.site.register(Cuenta, CuentaAdmin)

# Register your models here.
