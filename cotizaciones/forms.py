from django import forms
from cotizaciones.models import Cotizacion
from django.forms.widgets import Widget
from django.forms import widgets


class CotizacionForm(forms.ModelForm):

    class Meta:
        model = Cotizacion
    
    def clean_fecha(self):
        if Cotizacion.objects.filter(fecha=self.cleaned_data['fecha'],pais=self.cleaned_data['pais']).count() >0:
            raise forms.ValidationError("Ya existe una cotizacion en este dia!")
        return self.cleaned_data['fecha']
    def clean_monto(self):
        if self.cleaned_data['monto'] == 0:
            raise forms.ValidationError("El monto debe ser mayor a Cero!")
        return self.cleaned_data['monto']
