#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db.models.aggregates import Count
from django.shortcuts import render, render_to_response

# Create your views here.
from django.template.context import RequestContext
from django.utils.formats import number_format
from asientos_contables.models import AsientoContableDetalle
from cuentas.models import Cuenta
from ejercicios.models import Ejercicio
from hijasdelacaridad.globales import execute_all_query
from presupuestos.models import Presupuesto, MESES


def presupuesto(request,tipo):
    if tipo != 'IN' and tipo !='EG':
        tipo='IN'

    ejercicio=Ejercicio.objects.get(actual=True)
    presupuestos=Presupuesto.objects.filter(ejercicio_id=ejercicio.id).order_by('mes','cuenta__cuenta')

    query="select c.id, c.cuenta, p.mes,sum(p.monto) as monto from presupuestos_presupuesto p"\
    " join ejercicios_ejercicio e on e.id=p.ejercicio_id join cuentas_cuenta c on c.id=p.cuenta_id "\
    " where e.anho = "+str(ejercicio.anho)+" and c.tipo like '"+tipo+"' group by c.id, c.cuenta,p.mes order by c.cuenta"
    cuentas=execute_all_query(query)
    meses= MESES
    print meses[0][1]
    cuentas_list=[]

    i=0
    while i < len(cuentas):
        aux = [cuentas[i][0], cuentas[i][1]]
        for j in range(i, i+12):
            aux.append(str(cuentas[j][3]))
        cuentas_list.append(aux)
        i+=12
    if request.method == 'POST':
        for c in cuentas_list:
            for k in range(1,13):
                monto=request.POST.get('cuenta-'+str(c[0])+'-'+str(k))
                p=Presupuesto.objects.get(cuenta_id=c[0],mes=k,ejercicio_id=ejercicio.id)
                p.monto=monto
                p.save()
    return render_to_response('balance/presupuesto.html', {'cuentas_list':cuentas_list,'presupuestos':presupuestos,'tipo':tipo, 'MESES':MESES}, context_instance=RequestContext(request))



