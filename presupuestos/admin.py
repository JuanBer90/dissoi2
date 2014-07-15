from django.contrib import admin
from presupuestos.models import Presupuesto

class PresupuestoAdmin(admin.ModelAdmin):

    
    list_display = ('ejercicio','mes','cuenta','monto')
    
admin.site.register(Presupuesto, PresupuestoAdmin)

# Register your models here.
