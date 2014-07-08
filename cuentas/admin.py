from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from cuentas.models import Cuenta
from ajax_select.admin import AjaxSelectAdmin

class CuentaAdmin(TreeAdmin):
    form = movenodeform_factory(Cuenta)
    list_display = ('cuenta', 'tipo','have_child')
    list_filter = ['cuenta']
    
	        
admin.site.register(Cuenta, CuentaAdmin)

# Register your models here.
