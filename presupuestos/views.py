#!/usr/bin/python
# -*- coding: utf-8 -*-
from random import randrange
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models.aggregates import Count
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.shortcuts import get_object_or_404

# Create your views here.
from django.template.context import RequestContext
from comunidades.models import Comunidad, Pais
from cuentas.models import Cuenta
from ejercicios.models import Ejercicio
from hijasdelacaridad.globales import execute_all_query,USUARIO_LIMITADO,get_comunidad
from presupuestos.models import Presupuesto, MESES
from decimal import Decimal



def ver_presupuesto(request):
    app_label='Presupuesto'
    url="/admin/"
    if request.method == 'POST':
        id_comunidad=request.POST.get('comunidad_set-0-comunidad','')
        return HttpResponseRedirect('/presupuesto_comunidad/'+str(id_comunidad)+'/IN/')
    return render_to_response('balance/sel_comunidad.html',{'app_label':app_label,'url':url},
                                  context_instance=RequestContext(request))
def presupuesto_comunidad(request,id,tipo):
    print "id: "+str(id)
    if tipo != 'IN' and tipo !='EG':
        tipo='IN'
    cuentas=Cuenta.objects.filter(tipo=tipo).order_by('codigo_ordenado')
    usuario=request.user
    
    if int(id)==0 and usuario.is_superuser:
        messages.error(request, 'Debe ingresar una comunidad')
        return HttpResponseRedirect('/admin')
    if usuario.has_perm(USUARIO_LIMITADO):
        if int(id) != int(get_comunidad(usuario)):
            messages.error(request, 'No Pertenece a la Comunidad a la que desea Acceder!')
            return HttpResponseRedirect('/admin')
    if id == 0:
        comunidad=Comunidad.objects.get(pk=request.user.get_comunidad())
    else:
        comunidad=get_object_or_404(Comunidad,pk=id)
    ejercicio=Ejercicio.objects.get(actual=True)
    query="select c.id, c.cuenta, p.mes,sum(p.monto) as monto,c.codigo from presupuestos_presupuesto p"\
    " join ejercicios_ejercicio e on e.id=p.ejercicio_id join cuentas_cuenta c on c.id=p.cuenta_id "\
    " where e.anho = "+str(ejercicio.anho)+" and p.comunidad_id = "+str(comunidad.id)+" and c.tipo like '"+tipo+"' group by c.id, c.cuenta,c.codigo,p.mes order by c.codigo_ordenado, p.mes"
    print query
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
    for c in presupuestos_list:
        print c

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
            
   
    if request.method == 'POST':
        for c in presupuestos_list:
            for k in range(1,13):
                monto=request.POST.get('cuenta-'+str(c[0])+'-'+str(k))
                cambiar = request.POST.get('cambiar-' + str(c[0])+'-'+str(k),'')
                if cambiar == "true":
                    print 'cambiaar: ' + str(cambiar)+'  monto: '+str(monto)
                    print ' monto: '+str(monto)+'   cuenta: '+str(c[0])+' comunidad: '+str(comunidad)+' mes:'+str(k)+' ejercicio_id: '+str(ejercicio.id)    
                    p=Presupuesto.objects.get(cuenta_id=c[0],mes=k,ejercicio_id=ejercicio.id,comunidad=comunidad)
                    print p.comunidad.comunidad
                    p.monto=Decimal(monto)
                    p.save()
                    print 'guardado'
        messages.info(request, 'Grabado exitosamente!')
        save_=request.POST.get('_save','')
        continue_=request.POST.get('_continue','')
        return HttpResponseRedirect('/presupuesto_comunidad/'+str(id)+"/"+tipo)
    return render_to_response('balance/presupuesto.html', {'presupuestos_list':cuentas_list,'tipo':tipo,
                                                        'comunidad':comunidad, 'MESES':MESES}, context_instance=RequestContext(request))


def esta_en_presupuesto_list(id,presupuesto_list=[]):
    for p in presupuesto_list:
        if p[0] == id:
            return p
    return None

def ejecucion_presupuestaria(request,tipo):
    if tipo != 'IN' and tipo != 'EG':
        tipo = 'IN'
    ejercicio=Ejercicio.objects.get(actual=True)
    query_ejecutados="select c.id,c.cuenta, (extract(month from fecha) :: int) as mes, "\
    " (case when c.tipo like 'IN' then sum(haber)-sum(debe) else sum(debe)-sum(haber) end) as saldo, "\
    "  c.codigo from  asientos_contables_asientocontabledetalle ad "\
    " join asientos_contables_asientocontable a on a.id=ad.asiento_contable_id "\
    " join cuentas_cuenta c on c.id=ad.cuenta_id join ejercicios_ejercicio e on e.anho=extract(year from a.fecha) "\
    " where e.actual is true and c.tipo = '"+str(tipo)+"' group by extract(month from a.fecha),c.cuenta,c.id,c.codigo, "\
    " c.codigo_ordenado,c.tipo order by c.codigo_ordenado"
    ejecutados=execute_all_query(query_ejecutados)

    query_presupuestados = "select c.id, c.cuenta, p.mes,sum(p.monto) as monto,c.codigo from presupuestos_presupuesto p" \
            " join ejercicios_ejercicio e on e.id=p.ejercicio_id join cuentas_cuenta c on c.id=p.cuenta_id " \
            " where e.anho = " + str(ejercicio.anho) + " and c.tipo like '" + tipo + "' group by c.id, c.cuenta,c.codigo,p.mes" \
            " order by c.codigo_ordenado, mes"
    presupuestados = execute_all_query(query_presupuestados)

    presupuestados_list=[]
    i=0
    while i < len(presupuestados):
        aux = [presupuestados[i][0], presupuestados[i][1]]
        for j in range(i, i + 12):
            aux.append(str(presupuestados[j][3]))
        aux.append(presupuestados[i][4])
        presupuestados_list.append(aux)
        i += 12
    i=0

    ejecutados_list=[]
    while i<len(ejecutados):
        aux=[ejecutados[i][0],ejecutados[i][1]]
        for j in range(1,13):
            existe=get_monto_from_ejecutados(ejecutados[i][0],j,ejecutados)
            aux.append(existe)
        aux.append(ejecutados[i][4])
        ejecutados_list.append(aux)
        i+=1
    total_list=join_lists(presupuestados_list,ejecutados_list)


    cuentas=Cuenta.objects.filter(tipo=tipo).order_by('codigo_ordenado')
    cuentas_list = []
    for c in cuentas:
        existe=existe_en_lista(c.id,lista=total_list)
        if existe == None:
            aux=[c.id,c.cuenta]
            for i in range(2,26):
                aux.append('0.00')
            aux.append(c.codigo)
            aux.append(True)
            aux.append('no')
            cuentas_list.append(aux)
        else:
            existe.append(False)
            existe.append('si')
            cuentas_list.append(existe)
    sumar_padre(cuentas_list)
    url='/ejecucion_presupuestaria/'
    return render_to_response('balance/ejecucion_presupuestaria.html', {'url':url,'vector_cuentas':cuentas_list,'tipo':tipo,'meses':MESES},
                              context_instance=RequestContext(request))

def ejecucion_presupuestaria_comunidad(request,tipo):
    if tipo != 'IN' and tipo != 'EG':
        tipo = 'IN'
    id_comunidad=get_comunidad(request.user)
    if id_comunidad == 0:
        return HttpResponseRedirect('/admin')
    comunidad=Comunidad.objects.get(pk=id_comunidad)
    ejercicio=Ejercicio.objects.get(actual=True)
    query_ejecutados="select c.id,c.cuenta, (extract(month from fecha) :: int) as mes, "\
    " (case when c.tipo like 'IN' then sum(haber)-sum(debe) else sum(debe)-sum(haber) end) as saldo, "\
    "  c.codigo from  asientos_contables_asientocontabledetalle ad "\
    " join asientos_contables_asientocontable a on a.id=ad.asiento_contable_id "\
    " join cuentas_cuenta c on c.id=ad.cuenta_id join ejercicios_ejercicio e on e.anho=extract(year from a.fecha) "\
    " where e.actual is true and c.tipo = '"+str(tipo)+"' and a.comunidad_id = "+str(comunidad.id)+" group by extract(month from a.fecha),c.cuenta,c.id,c.codigo, "\
    " c.codigo_ordenado,c.tipo order by c.codigo_ordenado"
    ejecutados=execute_all_query(query_ejecutados)


    query_presupuestados = "select c.id, c.cuenta, p.mes,sum(p.monto) as monto,c.codigo from presupuestos_presupuesto p" \
            " join ejercicios_ejercicio e on e.id=p.ejercicio_id join cuentas_cuenta c on c.id=p.cuenta_id " \
            " where e.anho = " + str(ejercicio.anho) + " and c.tipo like '" + tipo + "' and p.comunidad_id="+str(comunidad.id)+" group by c.id, c.cuenta,c.codigo,p.mes" \
            " order by c.codigo_ordenado, mes"
    presupuestados = execute_all_query(query_presupuestados)

    presupuestados_list=[]
    i=0
    while i < len(presupuestados):
        aux = [presupuestados[i][0], presupuestados[i][1]]
        for j in range(i, i + 12):
            aux.append(str(presupuestados[j][3]))
        aux.append(presupuestados[i][4])
        presupuestados_list.append(aux)
        i += 12
    i=0

    ejecutados_list=[]
    while i<len(ejecutados):
        aux=[ejecutados[i][0],ejecutados[i][1]]
        for j in range(1,13):
            existe=get_monto_from_ejecutados(ejecutados[i][0],j,ejecutados)
            aux.append(existe)
        aux.append(ejecutados[i][4])
        ejecutados_list.append(aux)
        i+=1
    total_list=join_lists(presupuestados_list,ejecutados_list)


    cuentas=Cuenta.objects.filter(tipo=tipo).order_by('codigo_ordenado')
    cuentas_list = []
    for c in cuentas:
        existe=existe_en_lista(c.id,lista=total_list)
        if existe == None:
            aux=[c.id,c.cuenta]
            for i in range(2,26):
                aux.append('0.00')
            aux.append(c.codigo)
            aux.append(True)
            aux.append('no')
            cuentas_list.append(aux)
        else:
            existe.append(False)
            existe.append('si')
            cuentas_list.append(existe)
    sumar_padre(cuentas_list)
    url='/ejecucion_presupuestaria_comunidad/'
    return render_to_response('balance/ejecucion_presupuestaria.html', {'url':url,' vector_cuentas':cuentas_list,'tipo':tipo,
                                                                        'meses':MESES,'comunidad':comunidad},
                              context_instance=RequestContext(request))

def get_monto_from_ejecutados(id,mes,ejecutados=[]):
    for i in range(len(ejecutados)):
        if ejecutados[i][0] == id and ejecutados[i][2] == mes:
            return ejecutados[i][3]
    return 0.00

def existe_en_lista(id,lista=[]):
    for i in range(len(lista)):
        if lista[i][0] == id:
            return lista[i]
    return None

def join_lists(presupuestados,ejecutados):
    lista=[]
    for i in range(len(presupuestados)):
        aux=[presupuestados[i][0],presupuestados[i][1]]
        for j in range(2,len(presupuestados[0])-1):
            valor=get_valor(ejecutados,presupuestados[i][0],j)
            aux.append(valor)
            aux.append(presupuestados[i][j])
        aux.append(presupuestados[i][len(presupuestados[0])-1])
        lista.append(aux)
    return lista


def get_valor(ejecutados,id,pos):
    for i in range(len(ejecutados)):
        if ejecutados[i][0] == id:
            return  ejecutados[i][pos]
    return '0.00'

def sumar_padre(cuentas):
    for cuenta in cuentas:
            if cuenta[28] == 'si':
                codigo = cuenta[26].split(".")
                sumar(cuentas,cuenta,(".").join(codigo[0:len(codigo)-1]))

def sumar(cuentas,cuenta,padre):
    for c in cuentas:
        if c[26] == padre:
            for i in range(2, 26):
                c[i] = round(float(c[i]) + float(cuenta[i]), 2)
            if len(c[26])>1:
                codigo = c[26].split(".")
                sumar(cuentas,cuenta,(".").join(codigo[0:len(codigo) - 1]))
