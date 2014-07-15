#!/usr/bin/python
# -*- coding: utf-8 -*-
from decimal import Decimal
from time import timezone
import datetime
from twisted.test.test_amp import BadNoAnswerCommandProtocol
from django import forms
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from ajax_select.fields import AutoCompleteField
from django.template.defaultfilters import date
from django.views.generic.dates import timezone_today
from asientos_contables.models import AsientoContable, AsientoContableDetalle
from cotizaciones.models import Cotizacion
from cuentas.models import Cuenta
from cuentas.views import CuentasBalance
from cuentas_bancarias.models import CuentaBancaria
from usuarios.models import Usuario
from ejercicios.models import Ejercicio


class SearchForm(forms.Form):

    q = AutoCompleteField(
            'cliche',
            required=True,
            help_text="",
            label="Favori",
            attrs={'size': 100}
            )


def search_form(request):

    dd = {}
    if 'q' in request.GET:
        dd['entered'] = request.GET.get('q')
    initial = {'q': "\"This is an initial value,\" said O'Leary."}
    form = SearchForm(initial=initial)
    dd['form'] = form
    return render_to_response('search_form.html', dd, context_instance=RequestContext(request))


# Create your views here.
def nuevo(request):
    usuario_id = request.user.id
    usuario_objeto = User.objects.get(id=usuario_id)
    bancos = CuentaBancaria.objects.filter(comunidad=usuario_objeto.usuario.comunidad)
    print len(bancos)
    if request.method == 'POST':
        formulario=request.POST
        return render_to_response('balance/nuevo_change_form.html',
                                  {'add': True, 'bancos': bancos,'formulario':formulario, 'hoy': str(timezone_today().strftime('%d/%m/%Y'))},
                                  context_instance=RequestContext(request))
        addOther=request.POST.get('_addanother','').encode('utf8')
        save=request.POST.get('_save','')
        total_rows=int(request.POST.get('asientocontabledetalle_set-TOTAL_FORMS',0))
        fecha=request.POST.get('fecha','')
        fecha=datetime.datetime.strptime(fecha, "%d/%m/%Y")
        asiento = AsientoContable()
        asiento.fecha = fecha
        asiento.comunidad = usuario.comunidad
        asiento.save()
        for i in range(total_rows):
            id_cuenta = request.POST.get('asientocontabledetalle_set-' + str(i) + '-cuenta', '')
            debe = Decimal(request.POST.get('asientocontabledetalle_set-' + str(i) + '-debe', 0.00))
            haber = Decimal(request.POST.get('asientocontabledetalle_set-' + str(i) + '-haber', 0.00))
            if id_cuenta != '':
                id_cuenta=int(id_cuenta)
                cuenta=Cuenta.objects.get(pk=id_cuenta)
                asiento_detalle=AsientoContableDetalle()
                asiento_detalle.cuenta_id=id_cuenta
                asiento_detalle.debe=debe
                asiento_detalle.haber=haber
                asiento_detalle.asiento_contable=asiento
                if cuenta.codigo == '1.2.5.2':
                    banco_id = request.POST.get('asientocontabledetalle_set-' + str(i) + '-banco', 0)
                    asiento_detalle.cuenta_bancaria_id=banco_id
                asiento_detalle.save()
                print 'id_cuenta: '+str(id_cuenta)+'  debe: '+str(debe)+'  haber:  '+str(haber)
                if save == 'Grabar':
                    return HttpResponseRedirect('/asiento/listar/')
    return render_to_response('balance/nuevo_change_form.html', {'add':True,'bancos':bancos,'hoy':str(timezone_today().strftime('%d/%m/%Y'))},
                              context_instance=RequestContext(request))

def listar(request):
    asientos=AsientoContable.objects.all()
    return render_to_response('asientos/asientos_list.html', {'asientos':asientos}, context_instance=RequestContext(request))

def mayores(request):
    vector_cuentas = Cuenta.get_tree()
    
    usuario_id = request.user.id
    usuario_objeto = User.objects.get(id=usuario_id)
    usuario_comunidad_id = usuario_objeto.usuario.comunidad.id 


#Optimizar la consulta   
    for cuenta in vector_cuentas:
        if cuenta.numchild == 0:
            cuenta_id = cuenta.id
            asientos = AsientoContableDetalle.objects.filter(cuenta=cuenta_id)
            for asiento in asientos:
                if asiento.comunidad_id() == usuario_comunidad_id:
                    print 'asiento_comunidad: '+str(asiento.comunidad_id())+'  usuario_comunidad: '+str(usuario_comunidad_id)
                    cuenta.debe += asiento.debe
                    cuenta.haber += asiento.haber
            cuenta.cargado = True


    seguir = True
    longitud = len(vector_cuentas)
  
    while seguir:
        contador = 0
        for cuenta in vector_cuentas:
            if cuenta.cargado == False:
                debe = 0
                haber = 0
                hijos = cuenta.get_children()
                cargar = True
                salir = False
                for hijo in hijos:
                    for cuenta_aux in vector_cuentas:
                        if cuenta_aux.id == hijo.id:
                            if cuenta_aux.cargado:
                                debe += cuenta_aux.debe
                                haber += cuenta_aux.haber
                            else:
                                cargar = False
                                salir = True
                                break
                    if salir:
                        break
                if cargar:
                    cuenta.debe = debe
                    cuenta.haber = haber
                    cuenta.cargado = True
            else:
                contador += 1
        if contador == longitud:
            seguir = False

    return render_to_response('balance/mayores.html', {'vector_cuentas':vector_cuentas}, context_instance=RequestContext(request))


def mayor(request,tipo):
    vector_cuentas = Cuenta.objects.filter(tipo=tipo).order_by('codigo')
    usuario_id = request.user.id
    usuario_objeto = User.objects.get(id=usuario_id)
    usuario_comunidad_id = usuario_objeto.usuario.comunidad.id
    ejercicio = Ejercicio.objects.get(actual=True)
    anho = ejercicio.anho

#Optimizar la consulta
    for cuenta in vector_cuentas:
        if cuenta.numchild == 0:
            cuenta_id = cuenta.id
            asientos = AsientoContableDetalle.objects.filter(cuenta=cuenta_id)
            for asiento in asientos:
                if asiento.comunidad_id() == usuario_comunidad_id and asiento.anho == anho:
                    cuenta.debe += asiento.debe
                    cuenta.haber += asiento.haber
            cuenta.cargado = True


    seguir = True
    longitud = len(vector_cuentas)

    while seguir:
        contador = 0
        for cuenta in vector_cuentas:
            if cuenta.cargado == False:
                debe = 0
                haber = 0
                hijos = cuenta.get_children()
                cargar = True
                salir = False
                for hijo in hijos:
                    for cuenta_aux in vector_cuentas:
                        if cuenta_aux.id == hijo.id:
                            if cuenta_aux.cargado:
                                debe += cuenta_aux.debe
                                haber += cuenta_aux.haber
                            else:
                                cargar = False
                                salir = True
                                break
                    if salir:
                        break
                if cargar:
                    cuenta.debe = debe
                    cuenta.haber = haber
                    cuenta.cargado = True
            else:
                contador += 1
        if contador == longitud:
            seguir = False

    return render_to_response('balance/mayores.html', {'vector_cuentas':vector_cuentas,'tipo':tipo}, context_instance=RequestContext(request))

def mayor_general(request,tipo):
    vector_cuentas = Cuenta.objects.filter(tipo=tipo).order_by('codigo')
    usuario_id = request.user.id
    usuario_objeto = User.objects.get(id=usuario_id)
    usuario_comunidad_id = usuario_objeto.usuario.comunidad.id
    ejercicio = Ejercicio.objects.get(actual=True)
    anho = ejercicio.anho

#Optimizar la consulta
    for cuenta in vector_cuentas:
        if cuenta.numchild == 0:
            cuenta_id = cuenta.id
            asientos = AsientoContableDetalle.objects.filter(cuenta=cuenta_id)
            for asiento in asientos:
                if asiento.anho == anho:
                    cuenta.debe += asiento.debe_en_dolares()
                    cuenta.haber += asiento.haber_en_dolares()
            cuenta.cargado = True
            cuenta.debe = round(cuenta.debe,2)
            cuenta.haber = round(cuenta.haber,2)


    seguir = True
    longitud = len(vector_cuentas)

    while seguir:
        contador = 0
        for cuenta in vector_cuentas:
            if cuenta.cargado == False:
                debe = 0
                haber = 0
                hijos = cuenta.get_children()
                cargar = True
                salir = False
                for hijo in hijos:
                    for cuenta_aux in vector_cuentas:
                        if cuenta_aux.id == hijo.id:
                            if cuenta_aux.cargado:
                                debe += cuenta_aux.debe
                                haber += cuenta_aux.haber
                            else:
                                cargar = False
                                salir = True
                                break
                    if salir:
                        break
                if cargar:
                    cuenta.debe = debe
                    cuenta.haber = haber
                    cuenta.cargado = True
            else:
                contador += 1
        if contador == longitud:
            seguir = False

    return render_to_response('balance/mayores.html', {'vector_cuentas':vector_cuentas,'tipo':tipo}, context_instance=RequestContext(request))