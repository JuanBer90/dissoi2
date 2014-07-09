from django.contrib import admin
from cotizaciones.models import Cotizacion

class CotizacionAdmin(admin.ModelAdmin):
    list_dsplay = ('fecha','pais','monto')
    list_filter = ['pais','fecha']
    
admin.site.register(Cotizacion, CotizacionAdmin)