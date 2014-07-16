#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models.aggregates import Count
from django.http.response import HttpResponseRedirect
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
    cuentas=Cuenta.objects.filter(tipo=tipo).order_by('codigo','numchild')
    ejercicio=Ejercicio.objects.get(actual=True)

    query="select c.id, c.cuenta, p.mes,sum(p.monto) as monto,c.codigo from presupuestos_presupuesto p"\
    " join ejercicios_ejercicio e on e.id=p.ejercicio_id join cuentas_cuenta c on c.id=p.cuenta_id "\
    " where e.anho = "+str(ejercicio.anho)+" and c.tipo like '"+tipo+"' group by c.id, c.cuenta,c.codigo,p.mes order by c.cuenta"

    presupuestos=execute_all_query(query)
    presupuestos_list=[]

    cuentas_list=[]
    i=0

    while i < len(presupuestos):
        aux = [presupuestos[i][0], presupuestos[i][1]]
        for j in range(i, i+12):
            aux.append(str(presupuestos[j][3]))
        aux.append(presupuestos[i][4])
        presupuestos_list.append(aux)
        i+=12

    for c in cuentas:
        existe=esta_en_presupuesto_list(c.id, presupuestos_list)
        if existe != None:
            existe.append(False)
            cuentas_list.append(existe)
        else:
            aux = [c.id, c.cuenta]
            for ii in range(1, 13):
                aux.append('0.00')
            aux.append(c.codigo)
            aux.append(True)
            cuentas_list.append(aux)
    for asdf in cuentas_list:
        print asdf
    if request.method == 'POST':
        for c in presupuestos_list:
            for k in range(1,13):
                monto=request.POST.get('cuenta-'+str(c[0])+'-'+str(k))
                p=Presupuesto.objects.get(cuenta_id=c[0],mes=k,ejercicio_id=ejercicio.id)
                p.monto=monto
                p.save()
        messages.info(request, 'Grabado exitosamente!')
        save_=request.POST.get('_save','')
        continue_=request.POST.get('_continue','')
        if save_ != '':
            return HttpResponseRedirect('/admin/presupuestos/presupuesto/')
        if continue_ != '':
            return HttpResponseRedirect('/presupuesto/'+tipo)


    return render_to_response('balance/presupuesto.html', {'presupuestos_list':cuentas_list,'tipo':tipo, 'MESES':MESES}, context_instance=RequestContext(request))


def esta_en_presupuesto_list(id,presupuesto_list=[]):
    for p in presupuesto_list:
        if p[0] == id:
            return p
    return None
