from django.contrib import admin
from ejercicios.models import Ejercicio
from presupuestos.models import Presupuesto
from cuentas.models import Cuenta

class EjercicioAdmin(admin.ModelAdmin):
    #def save_related(self, request,form, formsets, change):
    def save_model(self, request, ejercicio, form, change):
        ejercicio.save()
        cuentas = Cuenta.objects.filter(numchild=0,tipo='IN').order_by('codigo')
        for cuenta in cuentas:
            for i in range(1,13):           
                presupuesto = Presupuesto()
                presupuesto.ejercicio = ejercicio   
                presupuesto.cuenta = cuenta
                presupuesto.mes = i
                presupuesto.monto = 0
                presupuesto.save()
        cuentas = Cuenta.objects.filter(numchild=0,tipo="EG").order_by('codigo')
        for cuenta in cuentas:
            for i in range(1,13):           
                presupuesto = Presupuesto()
                presupuesto.ejercicio = ejercicio   
                presupuesto.cuenta = cuenta
                presupuesto.mes = i
                presupuesto.monto = 0
                presupuesto.save()
    
    list_display = ('anho','actual')
    
admin.site.register(Ejercicio, EjercicioAdmin)
# Register your models here.
