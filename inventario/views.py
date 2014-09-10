from django.shortcuts import render
from django import forms
from inventario.models import Categoria, CategoriaDetalle, CategoriaDetalleMovimiento, TIPO_MOVIMIENTO
from django.shortcuts import render_to_response
from django.template import RequestContext
from inventario.forms import PrecioForm,MovimientoForm
from django.http.response import HttpResponseRedirect
from comunidades.models import Comunidad
import datetime
import decimal
from django.contrib import messages
from hijasdelacaridad.globales import execute_all_query,USUARIO_LIMITADO,get_comunidad
from django.views.generic.dates import timezone_today
from django.utils.datetime_safe import date
# Create your views here.

def seleccionar_comunidad(request):
    app_label="Inventario"
    url="/inventario/comunidad"
    if request.method == 'POST':
        id_comunidad=request.POST.get('comunidad_set-0-comunidad','')
        return HttpResponseRedirect('/inventario/categoria/'+str(id_comunidad))
    return render_to_response('balance/sel_comunidad.html',{'app_label':app_label,'url':url},
                                  context_instance=RequestContext(request))
def inventario_general(request):
    usuario=request.user
    if usuario.has_perm(USUARIO_LIMITADO):
        return HttpResponseRedirect('/admin')
    
    query="select  c.id,c.nombre,(sum(cd.cantidad)::int) as cantidad ,"\
    " round(sum(cd.precio_unitario/cot.monto),2) as total from inventario_categoria c"\
    " join inventario_categoriadetalle cd on cd.categoria_id = c.id "\
    " join comunidades_comunidad com on com.id=cd.comunidad_id "\
    " join cotizaciones_cotizacion cot on cot.pais_id=com.pais_id "\
    " group by c.id, c.nombre "
    categorias=execute_all_query(query)

    return render_to_response('balance/inventario_general.html',
                              {'categorias':categorias,},
                                  context_instance=RequestContext(request))

    
    

def inventario_comunidad(request,id_comunidad,id=0):
    usuario=request.user
    if usuario.has_perm(USUARIO_LIMITADO):
        if get_comunidad(usuario) != int(id_comunidad):
            messages.error(request, 'No Pertenece a la Comunidad a la que desea Acceder!')
            return HttpResponseRedirect('/admin')
    categorias=Categoria.objects.all().order_by('nombre')
    comunidad=Comunidad.objects.get(pk=id_comunidad)
    if id == 0:
        id=categorias[0].id
    categoria_actual=Categoria.objects.get(pk=id)
    form=MovimientoForm
    categoria_detalles=CategoriaDetalle.objects.filter(comunidad_id=id_comunidad,categoria_id=id)
    return render_to_response('balance/inventario_comunidad.html',
                              {'categorias':categorias,'actual':categoria_actual,
                               'categoria_detalles':categoria_detalles,'form':form,'comunidad':comunidad},
                                  context_instance=RequestContext(request))


def categoria_detalle(request,id_comunidad,id_categoria,id=0):
    usuario=request.user
    if get_comunidad(usuario) != int(id_comunidad) and usuario.has_perm(USUARIO_LIMITADO):
        return HttpResponseRedirect('/admin')
    categoria=Categoria.objects.get(pk=id_categoria)
    
    if id == 0:
        categoria_detalle=CategoriaDetalle()
        categoria_detalle.descripcion=""
        modo="Registrar Descripcion"
        precio_unitario=PrecioForm()
    else:
        categoria_detalle=CategoriaDetalle.objects.get(pk=id)
        if int(categoria_detalle.categoria_id) != int(id_categoria):
            return HttpResponseRedirect('/admin')
        categoria_detalle.precio_unitario=str(categoria_detalle.precio_unitario)
        modo="Modificar Descripcion"
    if request.method == 'POST':            
            categoria_detalle.cantidad=int(request.POST.get('cantidad',0))
            categoria_detalle.precio_unitario=request.POST.get('precio_unitario',0.00)
            categoria_detalle.categoria_id=categoria.id
            categoria_detalle.descripcion = request.POST.get('descripcion','') 
            categoria_detalle.comunidad_id=id_comunidad
            if id != 0:
                categoria_detalle.id=id
            categoria_detalle.save()
            if id == 0:
                movimiento=CategoriaDetalleMovimiento()
                movimiento.movimiento='INI'
                movimiento.observacion="carga del stock inicial"
                movimiento.categoria_detalle=categoria_detalle
                movimiento.cantidad=categoria_detalle.cantidad
                fecha=request.POST.get('fecha')
                movimiento.fecha=datetime.datetime.strptime(fecha, "%d/%m/%Y")
                movimiento.save()
               
            
            return HttpResponseRedirect('/inventario/categoria/'+str(id_comunidad)+'/'+str(categoria.id))
    
    return render_to_response('balance/categoria_detalle.html',
                              {'categoria_detalle':categoria_detalle,'categoria':categoria,
                               'modo':modo,'id_comunidad':id_comunidad},
                                  context_instance=RequestContext(request))
    
    
    
    
def movimiento_list(request,id_detalle):   
    movimientos=CategoriaDetalleMovimiento.objects.filter(categoria_detalle_id=id_detalle)
    detalle=CategoriaDetalle.objects.get(pk=id_detalle)
    usuario=request.user
    if usuario.has_perm(USUARIO_LIMITADO):
        if get_comunidad(usuario) != detalle.comunidad_id:
            return HttpResponseRedirect('/admin')
    return render_to_response('balance/movimiento_list.html',
                              {'movimientos':movimientos,'detalle':detalle},
                                  context_instance=RequestContext(request))
 
def movimiento(request,id_detalle,id=0):
    detalle=CategoriaDetalle.objects.get(pk=id_detalle)
    usuario=request.user
    
    if get_comunidad(usuario) != detalle.comunidad_id and usuario.has_perm(USUARIO_LIMITADO):
        return HttpResponseRedirect('/admin')
    if id == 0:
        movimiento=CategoriaDetalleMovimiento()
        movimiento.observacion=""
        modo="Registrar Movimiento"
    else:
        movimiento=CategoriaDetalleMovimiento.objects.get(pk=id)
        modo="Modificar Movimiento"
    if request.method == 'POST':
            movimiento.cantidad=int(request.POST.get('cantidad',0))
            movimiento.categoria_detalle_id=id_detalle
            movimiento.observacion=request.POST.get('observacion',0)
            movimiento.movimiento=request.POST.get('movimiento','INI')
            fecha=request.POST.get('fecha','')
            fecha=datetime.datetime.strptime(fecha, "%d/%m/%Y")
            movimiento.fecha=fecha
            if id != 0:
                movimiento.id=id
            movimiento.save()
            if movimiento.movimiento == 'ENT':
                detalle.cantidad+=movimiento.cantidad
            elif movimiento.movimiento == 'SAL':
                detalle.cantidad-=movimiento.cantidad
            else:
                detalle.cantidad=movimiento.cantidad
            detalle.save()
            
            return HttpResponseRedirect('/inventario/movimiento_list/'+str(detalle.id))
    
    return render_to_response('balance/movimiento.html',
                              {'detalle':detalle,'modo':modo,'tipo_movimientos':TIPO_MOVIMIENTO,'movimiento':movimiento},
                                context_instance=RequestContext(request)) 
   