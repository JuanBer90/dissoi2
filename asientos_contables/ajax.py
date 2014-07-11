from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from cotizaciones.models import Cotizacion
from cuentas.models import Cuenta



@dajaxice_register
def args_example(request, id,i):
    id=int(id)
    cuenta=Cuenta.objects.get(pk=id)
    return simplejson.dumps({'tipo':cuenta.tipo,'id':str(id),'i':i})
@dajaxice_register
def existe_cambio(request,fecha):
    Cotizacion.objects.filter(fecha=fecha)