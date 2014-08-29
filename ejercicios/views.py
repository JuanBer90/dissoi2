from django.db.models.query_utils import Q
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, render_to_response

# Create your views here.
from django.template.context import RequestContext
from django.views.generic.dates import timezone_today
from asientos_contables.models import AsientoContableDetalle, AsientoContable
from comunidades.models import Comunidad
from cuentas.models import Cuenta
from ejercicios.models import Ejercicio
from hijasdelacaridad.globales import execute_all_query
from presupuestos.models import Presupuesto

def ejercicio_actual(request):
    if Ejercicio.objects.filter(actual=True).exists():
        ejercicio=Ejercicio.objects.get(actual=True)
    else:
        ejercicio=Ejercicio()
    return render_to_response('balance/ver_ejercicio.html', {'ejercicio': ejercicio},
                              context_instance=RequestContext(request))

def set_ejercicio(request):
    ejercicios=Ejercicio.objects.all()
    if request.method == "POST":
        anho=request.POST.get('ejercicio_select','')
        if anho != "":
            request.session['ejercicio']=anho
    return render_to_response('balance/ver_ejercicio.html', {'ejercicios': ejercicios},
                              context_instance=RequestContext(request))



def cerrar_ejercicio(request):
    if Ejercicio.objects.filter(actual=True).exists():
        ejercicio=Ejercicio.objects.get(actual=True)
    else:
        ejercicio=Ejercicio()
    if request.method == 'POST':
        ejercicio.actual=False
        ejercicio.save()
        crear_ejercicio=request.POST.get('crear_ejercicio','No')
        print crear_ejercicio
        if crear_ejercicio == 'Si':
            nuevo_ejercicio = Ejercicio()
            nuevo_ejercicio.actual = True
            nuevo_ejercicio.anho = ejercicio.anho + 1
            nuevo_ejercicio.save()
            cuentas = Cuenta.objects.filter(numchild=0).filter(Q(tipo='IN') | Q(tipo='EG')).order_by('codigo_ordenado')
            comunidades = Comunidad.objects.all()
            for comunidad in comunidades:
                for cuenta in cuentas:
                    print cuenta
                    for i in range(1, 13):
                        presupuesto = Presupuesto()
                        presupuesto.ejercicio = nuevo_ejercicio
                        presupuesto.cuenta = cuenta
                        presupuesto.mes = i
                        presupuesto.monto = 0
                        presupuesto.comunidad = comunidad
                        presupuesto.save()
            crear_asiento=request.POST.get('crear_asiento','No')
            if crear_asiento == 'Si':
                query_comunidad="select distinct co.id  from asientos_contables_asientocontabledetalle ad "\
                " join asientos_contables_asientocontable a on a.id=ad.asiento_contable_id "\
                " join comunidades_comunidad co on co.id=a.comunidad_id "\
                " join cuentas_cuenta c on c.id=ad.cuenta_id "\
                " where extract(year from a.fecha)="+str(ejercicio.anho)+" and ad.debe-ad.haber != 0"
                comunidades=execute_all_query(query_comunidad)

                query="select co.id, c.id,sum(ad.debe)-sum(ad.haber) as saldo "\
                " from asientos_contables_asientocontabledetalle ad "\
                " join asientos_contables_asientocontable a on a.id=ad.asiento_contable_id "\
                " join comunidades_comunidad co on co.id=a.comunidad_id "\
                " join cuentas_cuenta c on c.id=ad.cuenta_id "\
                " where extract(year from a.fecha)="+str(ejercicio.anho)+" and ad.debe-ad.haber != 0"\
                " group by co.id,c.id, c.cuenta order by co.id"
                asientos_detalles=execute_all_query(query)

                for com in comunidades:
                    asiento_apertura=AsientoContable()
                    asiento_apertura.fecha=timezone_today()
                    asiento_apertura.comunidad_id=com[0]
                    asiento_apertura.observacion="Asiento de apertura correspodiente al ejercicio actual"
                    asiento_apertura.save()
                    for ad in asientos_detalles:
                        if ad[2] == com[0]:
                            asiento_detalle_apertura=AsientoContableDetalle()
                            asiento_detalle_apertura.cuenta_id=ad[1]
                            if ad[2]>0:
                                asiento_detalle_apertura.debe=ad[2]
                            else:
                                asiento_detalle_apertura.haber = ad[2]*-1
                            asiento_detalle_apertura.asiento_contable=asiento_apertura
                            asiento_detalle_apertura.observacion="Asiento de apertura"
                            asiento_detalle_apertura.save()
        return HttpResponseRedirect('/admin')
    return render_to_response('balance/cerrar_ejercicio.html', {'ejercicio':ejercicio},
                              context_instance=RequestContext(request))