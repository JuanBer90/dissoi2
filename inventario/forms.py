from django.forms import ModelForm
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from inventario.models import CategoriaDetalleMovimiento, CategoriaDetalle
from django.contrib.admin import widgets
from mx.DateTime.DateTime import today
from django.conf.global_settings import TIME_ZONE, DECIMAL_SEPARATOR
from django.views.generic.dates import timezone_today
from hijasdelacaridad import settings
from datetimewidget.widgets import DateTimeWidget
from datetime import datetime, time
from bootstrap_toolkit.widgets import BootstrapDateInput
import datetime

class FechaForm(forms.Form):
    fecha = forms.DateField(widget=BootstrapDateInput(), initial=datetime.date.today)

class PrecioForm(ModelForm):
    class Meta:
        model= CategoriaDetalle
        fields=['precio_unitario']
    precio_unitario= forms.IntegerField(widget=forms.TextInput(attrs={'style': 'heigth: 50px','step':'0.01'}))
    
class MovimientoForm(ModelForm):
     class Meta:
        model = CategoriaDetalleMovimiento
        fields=['movimiento','observacion','cantidad']
     fecha=forms.DateField(widget=widgets.AdminDateWidget(attrs={'readonly':'readonly','value': str(timezone_today().strftime('%d/%m/%Y'))}))
     cantidad=forms.IntegerField(min_value=0,widget=forms.DateInput())
    
             
     def save(self, commit=True):
        instance = super(MovimientoForm, self).save(commit=False)
        return instance
    
class DetalleForm(ModelForm):
    class Meta:
        model=CategoriaDetalle
        fields=['descripcion','cantidad','precio_unitario','fecha']
    fecha=forms.DateField(widget=widgets.AdminDateWidget(attrs={'readonly':'readonly','value': str(timezone_today().strftime('%d/%m/%Y'))}))
    cantidad=forms.IntegerField(min_value=0)
    precio_unitario=forms.IntegerField(min_value=0)
    
    def save(self, commit=True):
        instance = super(DetalleForm, self).save(commit=False)
        return instance

class DetalleReadOnlyForm(ModelForm):
    class Meta:
        model=CategoriaDetalle
        fields=['descripcion','cantidad','precio_unitario','fecha']
    fecha=forms.DateField(widget=widgets.AdminDateWidget(attrs={'readonly':'readonly','value': str(timezone_today().strftime('%d/%m/%Y'))}))
    cantidad=forms.IntegerField(min_value=0,widget=forms.TextInput(attrs={'readonly':'readonly'}))
    precio_unitario=forms.IntegerField(min_value=0)
    
    def save(self, commit=True):
        instance = super(DetalleReadOnlyForm, self).save(commit=False)
        return instance

              