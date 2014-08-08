from django.contrib import admin
from django.db.models.query_utils import Q
from comunidades.models import Comunidad
from ejercicios.forms import EjercicioForm
from ejercicios.models import Ejercicio
from presupuestos.models import Presupuesto
from cuentas.models import Cuenta

class EjercicioAdmin(admin.ModelAdmin):
    #def save_related(self, request,form, formsets, change):
    def save_model(self, request, ejercicio, form, change):
        if ejercicio.actual == True and Ejercicio.objects.filter(actual=True).count()>0:
            ejercicio_actual=Ejercicio.objects.filter(actual=True)
            for e in ejercicio_actual:
                e.actual=False
                e.save()
        ejercicio.save()

        cuentas = Cuenta.objects.filter(numchild=0).filter(Q(tipo='IN') | Q(tipo='EG')).order_by('codigo_ordenado')
        comunidades=Comunidad.objects.all()
        for comunidad in comunidades:
            for cuenta in cuentas:
                print cuenta
                for i in range(1,13):
                    presupuesto = Presupuesto()
                    presupuesto.ejercicio = ejercicio
                    presupuesto.cuenta = cuenta
                    presupuesto.mes = i
                    presupuesto.monto = 0
                    presupuesto.comunidad=comunidad
                    presupuesto.save()


    list_display = ('anho','actual')
    form = EjercicioForm
admin.site.register(Ejercicio, EjercicioAdmin)
# Register your models here.
