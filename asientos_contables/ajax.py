from datetime import datetime
from django.db.models.sql.datastructures import Date
from django.template.defaultfilters import time
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.views.generic.dates import timezone_today
from comunidades.models import Pais, Comunidad
from cotizaciones.models import Cotizacion
from cuentas.models import Cuenta



@dajaxice_register
def args_example(request, id,i):
    id=int(id)
    cuenta=Cuenta.objects.get(pk=id)
    return simplejson.dumps({'tipo':cuenta.tipo,'id':str(id),'i':i})

@dajaxice_register
def existe_cambio(request,fecha):
    fecha = fecha.split('/')
    nueva_fecha=fecha[2]+"-"+fecha[1]+'-'+fecha[0]
    existe='true'
    cantidad=Cotizacion.objects.filter(fecha=nueva_fecha).count()
    if (cantidad == 0):
         existe='false'
    return simplejson.dumps({'existe':existe})
