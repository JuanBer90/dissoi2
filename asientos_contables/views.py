#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.admin.models import LogEntry,LogEntryManager
from django.contrib.contenttypes.models import ContentType
from calendar import calendar
import calendar
from decimal import Decimal
from time import timezone
import datetime
from twisted.test.test_amp import BadNoAnswerCommandProtocol
from django import forms
from django.contrib import messages
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from ajax_select.fields import AutoCompleteField
from django.template.defaultfilters import date
from django.views.generic.dates import timezone_today
from asientos_contables.models import AsientoContable, AsientoContableDetalle
from comunidades.models import Comunidad, Pais
from cotizaciones.models import Cotizacion
from cuentas.models import Cuenta
from cuentas_bancarias.models import CuentaBancaria
from hijasdelacaridad.globales import execute_all_query
from usuarios.models import Usuario
from ejercicios.models import Ejercicio
from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.core.paginator import Paginator

ITEMS_PER_PAGE=100


class SearchForm(forms.Form):
    q = AutoCompleteField(
            'cliche',
            required=True,
            help_text="",
            label="",
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

 



def sel_comunidad_asiento(request):
       
    if request.method == 'POST':
        id_comunidad=request.POST.get('comunidad_set-0-comunidad','')
        return HttpResponseRedirect('/asiento/nuevo/'+str(id_comunidad))
    return render_to_response('balance/sel_comunidad_asiento.html',{},
                                  context_instance=RequestContext(request))

def nuevo(request,id_comunidad=''): 
  
    if id_comunidad == '' and not request.user.is_superuser:
        id_comunidad = request.user.usuario.comunidad_id
    else:
        if not request.user.has_perm('can_add_asiento_contable') or id_comunidad == '':
            return HttpResponseRedirect('/admin')
    bancos = CuentaBancaria.objects.filter(comunidad_id=id_comunidad)
    
    if request.method == 'POST':
        addOther = request.POST.get('_addanother', '').encode('utf8')
        save=request.POST.get('_save','')
        total_rows=int(request.POST.get('cantidad_rows',0))
        print 'asdf: '+str(total_rows)
        fecha=request.POST.get('fecha','')
        fecha=datetime.datetime.strptime(fecha, "%d/%m/%Y")
        asiento = AsientoContable()
        asiento.fecha = fecha
        asiento.comunidad_id = id_comunidad
        asiento.save()

        
        fields=""
        for i in range(0,total_rows):
            id_cuenta = request.POST.get('asientocontabledetalle_set-' + str(i) + '-cuenta', '')
            debe = Decimal(request.POST.get('asientocontabledetalle_set-' + str(i) + '-debe', 0.00))
            haber = Decimal(request.POST.get('asientocontabledetalle_set-' + str(i) + '-haber', 0.00))
            obs = request.POST.get('asientocontabledetalle_set-' + str(i) + '-observacion', '')
            if id_cuenta != '':
                id_cuenta=int(id_cuenta)
                cuenta=Cuenta.objects.get(pk=id_cuenta)
                asiento_detalle=AsientoContableDetalle()
                asiento_detalle.cuenta_id=id_cuenta
                asiento_detalle.debe=debe
                asiento_detalle.haber=haber
                asiento_detalle.asiento_contable=asiento
                asiento_detalle.observacion=obs
                if cuenta.codigo == '1.2.5.2':
                    banco_id = request.POST.get('asientocontabledetalle_set-' + str(i) + '-banco', 0)
                    asiento_detalle.cuenta_bancaria_id=banco_id
                asiento_detalle.save()
                fields+='id:'+str(id_cuenta)+'-'+str(debe)+'-'+str(haber)+"\n"
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(AsientoContable).pk,
            object_id=asiento.id,
            object_repr=unicode(fields),
            action_flag=ADDITION)
    cuentas=Cuenta.objects.all()
    filas=[]
    for i in range(0,50):
         filas.append(i)
    if request.user.is_superuser:
        return render_to_response('balance/admin_change_form.html',
                                  {'add': True, 'filas':filas,'bancos': bancos, 'hoy': str(timezone_today().strftime('%d/%m/%Y'))},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('balance/nuevo_change_form.html', {'add':True,'filas':filas,'bancos':bancos,'hoy':str(timezone_today().strftime('%d/%m/%Y'))},
                              context_instance=RequestContext(request))


def editar(request,id):
    asiento=AsientoContable.objects.get(pk=id)
    asientos_detalles=AsientoContableDetalle.objects.filter(asiento_contable_id=id)
    if not request.user.is_superuser:
        id_comunidad = request.user.usuario.comunidad_id
    else:
        id_comunidad=asiento.comunidad_id
    usuario_id = request.user.id
    usuario_objeto = User.objects.get(id=usuario_id)
    bancos = CuentaBancaria.objects.filter(comunidad=usuario_objeto.usuario.comunidad)
    
    if request.method == 'POST':
        addOther=request.POST.get('_addanother','').encode('utf8')
        save=request.POST.get('_save','')
        total_rows=int(request.POST.get('cantidad_rows',0))
        fecha=request.POST.get('fecha','')
        fecha=datetime.datetime.strptime(fecha, "%d/%m/%Y")
        asiento.fecha = fecha
        asiento.save()

        for a in asientos_detalles:
           a.delete()
        fields=""
        for i in range(total_rows):            
            id_cuenta = request.POST.get('asientocontabledetalle_set-' + str(i) + '-cuenta', '')
            debe = Decimal(request.POST.get('asientocontabledetalle_set-' + str(i) + '-debe', 0.00))
            haber = Decimal(request.POST.get('asientocontabledetalle_set-' + str(i) + '-haber', 0.00))
            obs = request.POST.get('asientocontabledetalle_set-' + str(i) + '-observacion', '')
            print 'id_cuenta: '+str(id_cuenta)+'  debe: '+str(debe)+'  haber:  '+str(haber)+'  obs: '+str(obs)
            
            if id_cuenta != '':
                id_cuenta=int(id_cuenta)
                cuenta=Cuenta.objects.get(pk=id_cuenta)
                asiento_detalle=AsientoContableDetalle()
                asiento_detalle.cuenta_id=id_cuenta
                asiento_detalle.debe=debe
                asiento_detalle.haber=haber
                asiento_detalle.asiento_contable=asiento
                asiento_detalle.observacion=obs
                if cuenta.codigo == '1.2.5.2':
                    banco_id = request.POST.get('asientocontabledetalle_set-' + str(i) + '-banco', 0)
                    asiento_detalle.cuenta_bancaria_id=banco_id
                asiento_detalle.save()
                fields+='id:'+str(id_cuenta)+'-'+str(debe)+'-'+str(haber)+"\n"
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(AsientoContable).pk,
            object_id=asiento.id,
            object_repr=unicode(fields),
            action_flag=CHANGE)

        return HttpResponseRedirect('/asiento/editar/'+str(id))
        if save == 'Grabar':
                return HttpResponseRedirect('/asiento/listar/')
    filas=[]
    for i in range(len(asientos_detalles),50):
         filas.append(i)
    asiento.fecha=str(asiento.fecha.strftime('%d/%m/%Y'))
    if request.user.is_superuser:
        return render_to_response('balance/admin_edit_asiento.html',{'filas':filas,'bancos': bancos,
              'asiento':asiento, 'asientos_detalles':asientos_detalles}, context_instance=RequestContext(request))
    else:
        return render_to_response('balance/edit_change_form.html', {'asiento':asiento,'filas':filas,
           'asientos_detalles':asientos_detalles,'bancos':bancos}, context_instance=RequestContext(request))

def listar(request):
    
    q=request.GET.get('q','')
    fecha__gte=request.GET.get('fecha__gte','1900-01-01')
    fecha__lt=request.GET.get('fecha__lt','2050-01-01')
    usuario=request.user
    
    
    
    if usuario.is_superuser:
           objeto_total=AsientoContableDetalle.objects.filter(asiento_contable__fecha__contains=q,
                                                          asiento_contable__fecha__gt=fecha__gte,
                                                       asiento_contable__fecha__lt=fecha__lt).count()
    else:
        objeto_total=AsientoContableDetalle.objects.filter(asiento_contable__fecha__contains=q,
                                                          asiento_contable__fecha__gt=fecha__gte,
                                                       asiento_contable__fecha__lt=fecha__lt,asiento_contable__comunidad_id=usuario.usuario.comunidad_id).count()
    page=request.GET.get('page',1)
    
    lines=[]
    for i in range(objeto_total):
        lines.append(u'Line %s' % (i + 1))
    nro_lineas=100
    paginator = Paginator(lines, nro_lineas)
    try:
        page=int(page)
    except:
        page=1
    if int(page)*nro_lineas>objeto_total or int(page)>0:
        try:
            items = paginator.page(page)
            fin=int(page)*nro_lineas
            ini =fin-nro_lineas
        except PageNotAnInteger or EmptyPage:
            fin=nro_lineas
            ini=0
            items = paginator.page(1)
    else:
        fin=nro_lineas
        ini=0
        items = paginator.page(1)
        
    if usuario.is_superuser:
           asientos=AsientoContableDetalle.objects.filter(asiento_contable__fecha__contains=q,
                                                          asiento_contable__fecha__gt=fecha__gte,
                                                       asiento_contable__fecha__lt=fecha__lt)[ini:fin]
    else:
        asientos=AsientoContableDetalle.objects.filter(asiento_contable__fecha__contains=q,
                                                          asiento_contable__fecha__gt=fecha__gte,
                                                       asiento_contable__fecha__lt=fecha__lt,asiento_contable__comunidad_id=usuario.usuario.comunidad_id)

    hoy = datetime.datetime.today()
    ayer=hoy+datetime.timedelta(days=-1)
    ultimos_7dias = hoy + datetime.timedelta(days=-7)
    manana = hoy + datetime.timedelta(days=1)
    today=timezone_today()
    cant_dias=calendar.monthrange(today.year,1)[1]
    ultimos_30dias_max=str(today.year)+'-'+str(today.month)+'-'+str(cant_dias)
    ultimos_30dias_min = str(today.year) + '-' + str(today.month) + '-01'
    este_anho_max=str(today.year+1) + '-01-01'
    este_anho_min = str(today.year) + '-01-01'
    
    return render_to_response('asientos/nuevo_asientos_list.html',
    {'asientos':asientos,'hoy':str(hoy.date()),'ultimos_30dias_max':ultimos_30dias_max,'page' : page,
     'ayer':str(ayer.date()),'ultimos_30dias_min':ultimos_30dias_min,'este_anho_max':este_anho_max,'este_anho_min':este_anho_min
        ,'ultimo_7dias':str(ultimos_7dias.date()),'manana':str(manana.date())},
    context_instance=RequestContext(request,{ 'lines': items }))

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
                if asiento.comunidad_id() == usuario_comunidad_id and asiento.anho() == anho:
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

def mayor_general(request,tipo='AC'):
    tipos=['AC','PA','PN','IN','EG']
    if not tipos.__contains__(tipo):
        tipo='AC'
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
                if asiento.anho() == anho:
                    print 'debe: ' + str(asiento.cotizacion_del_dia())
                     #+ '   asfdasdf ' + str(asiento.debe_en_dolares())
                    cuenta.debe += asiento.debe_en_dolares()
                    cuenta.haber += asiento.haber_en_dolares()

            cuenta.cargado = True
            cuenta.debe = round(cuenta.debe,2)
            cuenta.haber = round(cuenta.haber,2)
            print 'debe: '+str(cuenta.debe)

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
    return render_to_response('balance/mayor_general.html', {'vector_cuentas':vector_cuentas,'tipo':tipo}, context_instance=RequestContext(request))

def mayor_detallado_comunidad(request,id,tipo='AC'):
    tipos = ['AC', 'PA', 'PN', 'IN', 'EG']
    if not tipos.__contains__(tipo):
        tipo = 'AC'
    if id == '':
        id_comunidad=request.user.usuario.comunidad.id
    ejercicio_anho = Ejercicio.objects.get(actual=True).anho
    query = " select distinct c.id,c.cuenta from cuentas_cuenta c " \
            " join asientos_contables_asientocontabledetalle ad on ad.cuenta_id = c.id " \
            " join asientos_contables_asientocontable a on a.id=ad.asiento_contable_id " \
            " where a.comunidad_id=" + str(id) + " and tipo='" + tipo + "'  and extract( year from a.fecha) ="+str(ejercicio_anho)
    cuentas_list = execute_all_query(query)
    asientos=AsientoContableDetalle.objects.filter(cuenta__tipo=tipo,asiento_contable__fecha__year=ejercicio_anho,asiento_contable__comunidad_id=id).order_by('cuenta__codigo')
    cuentas=[]
    for id_cuenta,cuenta in cuentas_list:
        debe=haber=0
        for asiento in asientos:
            if id_cuenta ==  asiento.cuenta_id:
                debe+=asiento.debe
                haber+=asiento.haber
        cuentas.append([id_cuenta,cuenta,debe-haber,asiento.cuenta.codigo])
    url='/mayor_detalle_comunidad/'+str(id)+'/'
    return render_to_response('balance/mayor_detallado.html', {'asientos': asientos,'url':url,'cuentas':cuentas, 'tipo': tipo},
                              context_instance=RequestContext(request))

def mayor_detallado_pais(request,id,tipo='AC'):
    tipos = ['AC', 'PA', 'PN', 'IN', 'EG']
    if not tipos.__contains__(tipo):
        tipo = 'AC'
    if id == '':
        id = request.user.usuario.comunidad_id
        pais = Comunidad.objects.get(pk=id).pais
    else:
        pais = Pais.objects.get(pk=id)
    ejercicio_anho=Ejercicio.objects.get(actual=True).anho
    query = " select distinct c.id,c.cuenta from cuentas_cuenta c " \
            " join asientos_contables_asientocontabledetalle ad on ad.cuenta_id = c.id " \
            " join asientos_contables_asientocontable a on a.id=ad.asiento_contable_id " \
            " join comunidades_comunidad co on co.id = a.comunidad_id " \
            " where co.pais_id=" + str(id) + " and tipo='" + tipo + "' and extract( year from a.fecha) ="+str(ejercicio_anho)


    cuentas_list = execute_all_query(query)
    query_asiento="select ad.* from  asientos_contables_asientocontabledetalle ad "\
    " join asientos_contables_asientocontable a on a.id=ad.asiento_contable_id "\
    " join cuentas_cuenta c on c.id = ad.cuenta_id "\
    " join comunidades_comunidad co on co.id = a.comunidad_id "\
    " where c.tipo = '"+tipo+"' and co.pais_id = "+str(id)+" and extract( year from a.fecha) ="+str(ejercicio_anho)+" "\
    " order by c.codigo"
    print query_asiento

    asientos = AsientoContableDetalle.objects.raw(query_asiento)

    cuentas=[]
    for id_cuenta,cuenta in cuentas_list:
        debe=haber=0
        for asiento in asientos:
            if id_cuenta ==  asiento.cuenta_id:
                debe+=asiento.debe
                haber+=asiento.haber
        cuentas.append([id_cuenta,cuenta,debe-haber,asiento.cuenta.codigo])
    url = '/mayor_detalle_pais/' + str(id) + '/'
    return render_to_response('balance/mayor_detallado.html', {'asientos': asientos,'url':url,'cuentas':cuentas, 'tipo': tipo},
                              context_instance=RequestContext(request))


def mayor_detallado_consolidado(request,tipo='AC'):
    tipos = ['AC', 'PA', 'PN', 'IN', 'EG']
    if not tipos.__contains__(tipo):
        tipo = 'AC'
    ejercicio_anho=Ejercicio.objects.get(actual=True).anho
    query_asiento="select distinct * from (select ad.* from  asientos_contables_asientocontabledetalle ad "\
    " join asientos_contables_asientocontable a on a.id=ad.asiento_contable_id "\
    " join cuentas_cuenta c on c.id = ad.cuenta_id "\
    " join cotizaciones_cotizacion cot on cot.fecha=a.fecha where c.tipo = '"+str(tipo)+"'" \
    " and extract( year from a.fecha) = "+str(ejercicio_anho)+" order by c.codigo) as T"


    asientos = AsientoContableDetalle.objects.raw(query_asiento)

    query_cuentas = " select distinct c.id,c.cuenta from cuentas_cuenta c " \
            " join asientos_contables_asientocontabledetalle ad on ad.cuenta_id = c.id " \
            " join asientos_contables_asientocontable a on a.id=ad.asiento_contable_id " \
            " where tipo='" + tipo + "' and extract( year from a.fecha) =" + str(ejercicio_anho)
    cuentas_list=execute_all_query(query_cuentas)
    cuentas = []
    for id_cuenta, cuenta in cuentas_list:
        debe = haber = 0
        for asiento in asientos:
            if id_cuenta == asiento.cuenta_id:
                debe += asiento.debe_en_dolares()
                haber += asiento.haber_en_dolares()
        cuentas.append([id_cuenta, cuenta, debe - haber, asiento.cuenta.codigo])
    print query_cuentas
    print cuentas
    url = '/mayor_detalle_consolidado/'
    return render_to_response('balance/mayor_detallado.html',
                              {'asientos': asientos, 'url': url, 'cuentas': cuentas, 'tipo': tipo,'consolidado':'true'},
                              context_instance=RequestContext(request))


def ver_mayor(request):
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
                return HttpResponseRedirect('/mayor_detalle_pais/'+str(id_pais)+'/AC')
        elif tipo == 'comunidad':
            id_comunidad = int(request.POST.get('comunidad', 0))
            if id_comunidad == 0:
                messages.error(request, 'Debe Seleccionar una comunidad!')
            else:
                return HttpResponseRedirect('/mayor_detalle_comunidad/' + str(id_comunidad)+'/AC')
        else:
            return HttpResponseRedirect('/mayor_detalle_consolidado/')
    return render_to_response('balance/ver_mayor.html',
                              {'comunidades':comunidades,'paises':paises},
                              context_instance=RequestContext(request))

def ver_mayor_detalle(request):
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
                return HttpResponseRedirect('/mayor_detalle_pais/'+str(id_pais)+'/AC')
        elif tipo == 'comunidad':
            id_comunidad = int(request.POST.get('comunidad', 0))
            if id_comunidad == 0:
                messages.error(request, 'Debe Seleccionar una comunidad!')
            else:
                return HttpResponseRedirect('/mayor_detalle_comunidad/' + str(id_comunidad)+'/AC')
        else:
            return HttpResponseRedirect('/mayor_detalle_consolidado/')
    return render_to_response('balance/ver_mayor.html',
                              {'comunidades':comunidades,'paises':paises},
                              context_instance=RequestContext(request))
