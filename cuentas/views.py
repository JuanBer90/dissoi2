#!/usr/bin/python
# -*- coding: utf-8 -*-
from string import split
from zope.interface.tests.test_declarations import test_that_we_dont_inherit_provides_optimizations
from django.contrib import messages
from django.db import connection, models
from django.db.models.query_utils import Q
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template.context import RequestContext
from comunidades.models import Comunidad, Pais
from cuentas.models import TIPOS_DE_CUENTA, Cuenta


def ver_balance(request):
    comunidades=Comunidad.objects.all()
    paises=Pais.objects.all()
    if request.method == 'POST':
        tipo=request.POST.get('tipo','')
        print tipo
        if tipo == 'pais':
            id_pais=int(request.POST.get('pais',0))
            if id_pais == 0:
                messages.error(request, 'Debe Seleccionar un pais!')
            else:
                return HttpResponseRedirect('/balance/pais/'+str(id_pais))
        elif tipo == 'comunidad':
            id_comunidad = int(request.POST.get('comunidad', 0))
            if id_comunidad == 0:
                messages.error(request, 'Debe Seleccionar una comunidad!')
            else:
                return HttpResponseRedirect('/balance/comunidad/' + str(id_comunidad))
        else:
            return HttpResponseRedirect('/balance/consolidado/')
    return render_to_response('balance/ver_balance.html',
                              {'comunidades':comunidades,'paises':paises},
                              context_instance=RequestContext(request))

def balance_comunidad(request,id):
    if id == '':
        id=request.user.usuario.comunidad_id
    comunidad=Comunidad.objects.get(pk=id)
    query="select (case when cuenta.tipo like 'AC' then 'ACTIVO' when cuenta.tipo like 'PA' then 'PASIVO' "\
    " when cuenta.tipo like 'IN' then 'INGRESOS' when cuenta.tipo like 'EG' then 'EGRESOS' else 'PATRIMONIO NETO' end) cuenta," \
    " sum(asiento_detalle.debe) as suma_debe, sum(asiento_detalle.haber) as suma_haber, "\
    " (case when sum(asiento_detalle.debe) > sum(asiento_detalle.haber)  then sum(asiento_detalle.debe)-sum(asiento_detalle.haber) else 0.00 end) deudor, "\
    " (case when sum(asiento_detalle.debe) < sum(asiento_detalle.haber)  then sum(asiento_detalle.haber) - sum(asiento_detalle.debe) else 0.00 end) acreedor, "\
    " (case when cuenta.tipo like 'AC'then sum(asiento_detalle.debe)-sum(asiento_detalle.haber) else 0.00 end) as activo, "\
    " (case when cuenta.tipo like 'PA'then sum(asiento_detalle.haber) - sum(asiento_detalle.debe) else 0.00 end) as pasivo, "\
    " (case when cuenta.tipo like 'EG'then sum(asiento_detalle.debe) else 0.00 end) as perdidas, "\
    " (case when cuenta.tipo like 'IN'then sum(asiento_detalle.haber) else 0.00 end) as ganancias "\
    " from asientos_contables_asientocontabledetalle as asiento_detalle "\
    " join asientos_contables_asientocontable asiento on asiento.id = asiento_detalle.asiento_contable_id "\
    " join cuentas_cuenta cuenta on cuenta.id = asiento_detalle.cuenta_id "\
    " where asiento.comunidad_id = "+str(id)+" and extract(year from asiento.fecha) = (select anho from ejercicios_ejercicio where actual is true)" \
    " group by  cuenta.tipo"

    cuentas=select_all(query)
    total=[]
    if cuentas:
        total.append('TOTAL')
        for i in range(1,len(cuentas[0])):
            suma=0
            for j in range(0,len(cuentas)):
                    suma+= cuentas[j][i]
            total.append(suma)
    return render(request, 'balance/balance.html', {'cuentas':cuentas,'TIPOS_DE_CUENTA':TIPOS_DE_CUENTA,'total':total, 'titulo':'Balance: '+str(comunidad.comunidad)})

def balance_pais(request,id):
    if id == '':
        id = request.user.usuario.comunidad_id
        pais =Comunidad.objects.get(pk=id).pais
    else:
        pais=Pais.objects.get(pk=id)
    query = "select (case when cuenta.tipo like 'AC' then 'ACTIVO' when cuenta.tipo like 'PA' then 'PASIVO' " \
            " when cuenta.tipo like 'IN' then 'INGRESOS' when cuenta.tipo like 'EG' then 'EGRESOS' else 'PATRIMONIO NETO' end) cuenta," \
            " sum(asiento_detalle.debe) as suma_debe, sum(asiento_detalle.haber) as suma_haber, " \
            " (case when sum(asiento_detalle.debe) > sum(asiento_detalle.haber)  then sum(asiento_detalle.debe)-sum(asiento_detalle.haber) else 0.00 end) deudor, " \
            " (case when sum(asiento_detalle.debe) < sum(asiento_detalle.haber)  then sum(asiento_detalle.haber) - sum(asiento_detalle.debe) else 0.00 end) acreedor, " \
            " (case when cuenta.tipo like 'AC'then sum(asiento_detalle.debe)-sum(asiento_detalle.haber) else 0.00 end) as activo, " \
            " (case when cuenta.tipo like 'PA'then sum(asiento_detalle.haber) - sum(asiento_detalle.debe) else 0.00 end) as pasivo, " \
            " (case when cuenta.tipo like 'EG'then sum(asiento_detalle.debe) else 0.00 end) as perdidas, " \
            " (case when cuenta.tipo like 'IN'then sum(asiento_detalle.haber) else 0.00 end) as ganancias " \
            " from asientos_contables_asientocontabledetalle as asiento_detalle " \
            " join asientos_contables_asientocontable asiento on asiento.id = asiento_detalle.asiento_contable_id " \
            " join comunidades_comunidad comunidad on comunidad.id = asiento.comunidad_id " \
            " join comunidades_pais pais on pais.id=comunidad.pais_id " \
            " join cuentas_cuenta cuenta on cuenta.id = asiento_detalle.cuenta_id " \
            " where pais.id= " + str(id) + " and extract(year from asiento.fecha) = (select anho from ejercicios_ejercicio where actual is true)" \
            " group by  cuenta.tipo"
    cuentas = select_all(query)
    total = []
    if cuentas:
        total.append('TOTAL')
        for i in range(1, len(cuentas[0])):
            suma = 0
            for j in range(0, len(cuentas)):
                suma += cuentas[j][i]
            total.append(suma)

    return render(request, 'balance/balance.html', {'TIPOS_DE_CUENTA': TIPOS_DE_CUENTA,'total':total,'titulo':'Balance: '+str(pais.pais),'cuentas':cuentas})

def balance_general(request):
    query="select (case when tipo like 'AC' then 'ACTIVO' when tipo like 'PA' then 'PASIVO' "\
    " when tipo like 'IN' then 'INGRESOS' when tipo like 'EG' then 'EGRESOS' else 'PATRIMONIO NETO' end) cuenta, "\
    " round(sum(debe),2) as suma_debe, round(sum(haber),2) as suma_haber, "\
    " (case when sum(debe) > sum(haber)  then round(sum(debe)-sum(haber),2) else 0.00 end) deudor, "\
    " (case when sum(debe) < sum(haber)  then round(sum(haber) - sum(debe),2) else 0.00 end) acreedor, "\
    " (case when tipo like 'AC'then round(sum(debe)-sum(haber),2) else 0.00 end) as activo, "\
    " (case when tipo like 'PA'then round(sum(haber) - sum(debe),2) else 0.00 end) as pasivo, "\
    " (case when tipo like 'EG'then round(sum(debe),2) else 0.00 end) as perdidas, "\
    " (case when tipo like 'IN'then round(sum(haber),2) else 0.00 end) as ganancias "\
    " from (select cuenta.tipo, asiento_detalle.debe/cot.monto debe, asiento_detalle.haber/cot.monto haber "\
    " from asientos_contables_asientocontabledetalle as asiento_detalle "\
    " join asientos_contables_asientocontable asiento on asiento.id = asiento_detalle.asiento_contable_id "\
    " join comunidades_comunidad comunidad on comunidad.id = asiento.comunidad_id "\
    " join comunidades_pais pais on pais.id=comunidad.pais_id "\
    " join cotizaciones_cotizacion cot on cot.pais_id = pais.id and cot.fecha = asiento.fecha "\
    " join cuentas_cuenta cuenta on cuenta.id = asiento_detalle.cuenta_id " \
    " where extract(year from asiento.fecha) = (select anho from ejercicios_ejercicio where actual is true)) as T" \
    " group by  tipo "
    cuentas=select_all(query)
    total = []
    if cuentas:
        total.append('TOTAL')
        for i in range(1, len(cuentas[0])):
            suma = 0
            for j in range(0, len(cuentas)):
                suma += cuentas[j][i]
            total.append(suma)

    return render(request, 'balance/balance.html', {'TIPOS_DE_CUENTA': TIPOS_DE_CUENTA,'total':total,'cuentas':cuentas,'titulo':'Balance Consolidado'})

def select_all(query):
    cursor=connection.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def prueba(request):
    
    return render(request, 'admin/index.html')