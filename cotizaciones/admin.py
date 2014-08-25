from django import forms
from django.contrib import admin
from cotizaciones.forms import CotizacionForm
from cotizaciones.models import Cotizacion
s="/admin/js/SeparadorDeMiles.js"


class CotizacionAdmin(admin.ModelAdmin):
    form=CotizacionForm
    list_dsplay = ('fecha','pais','monto')
    list_filter = ['pais','fecha']


admin.site.register(Cotizacion, CotizacionAdmin)