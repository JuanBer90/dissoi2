from django.shortcuts import render
from cuentas_bancarias.models import CuentaBancaria
from comunidades.models import Comunidad
from django.shortcuts import render_to_response
from django.template import RequestContext
from asientos_contables.models import AsientoContableDetalle
from hijasdelacaridad.globales import USUARIO_LIMITADO, get_comunidad
from django.http.response import HttpResponseRedirect

# Create your views here.
def cuentas_bancarias(request,id_comunidad,id_banco=''):
    print request.user.has_perm(USUARIO_LIMITADO)

    if request.user.has_perm(USUARIO_LIMITADO):
        if get_comunidad(request.user) != int(id_comunidad):
            return HttpResponseRedirect('/admin')
    bancos=CuentaBancaria.objects.filter(comunidad_id=id_comunidad)
    if id_banco == '':
         if len(bancos) > 0:
            actual=bancos[0]
         else:
            actual=CuentaBancaria(pk=0)
    else:
        actual=CuentaBancaria.objects.get(pk=id_banco)
    if actual.id == 0:
        asientos_contables=[]
    else: 
        asientos_contables=AsientoContableDetalle.objects.filter(asiento_contable__comunidad_id=id_comunidad,cuenta_bancaria_id=actual.id)
    if id_banco != '':
        actual=CuentaBancaria.objects.get(pk=id_banco)
    
    comunidad=Comunidad.objects.get(pk=id_comunidad)
    
    return render_to_response('balance/cuentas_bancarias.html', {'comunidad': comunidad,'bancos':bancos,
                        'actual':actual,'asientos_contables':asientos_contables},
                              context_instance=RequestContext(request))

def sel_comunidad_cuenta_bancaria(request):
    app_label='Cuentas Bancarias'
    url="/asiento/listar/"
    if request.method == 'POST':
        id_comunidad=request.POST.get('comunidad_set-0-comunidad','')
        return HttpResponseRedirect('/cuentas_bancarias/'+str(id_comunidad))
    return render_to_response('balance/sel_comunidad.html',{'app_label':app_label,'url':url},
                                  context_instance=RequestContext(request))

    
    

    