from django.contrib import admin
from ejercicios.models import Ejercicio

class EjercicioAdmin(admin.ModelAdmin):
    list_display = ('anho','actual')
    
admin.site.register(Ejercicio, EjercicioAdmin)
# Register your models here.
