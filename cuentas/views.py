#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import connection
from django.db.models.query_utils import Q
from django.http.response import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from asientos_contables.models import AsientoContableDetalle
from cuentas.admin import CuentaAdmin
from cuentas.lookups import CuentaLookup
from cuentas.models import Cuenta
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from treebeard.mp_tree import MP_Node


class CuentasBalance():
    cuenta= Cuenta
    debe=0.00
    haber=0.00
    procesado=False

def Balance(request):
    asientos_=AsientoContableDetalle.objects.all().order_by('cuenta__path')
    cuentas=Cuenta.get_tree()
    arbol_list=[]

    query="select cuenta_id,sum(debe) as debe,sum(haber) as haber "\
    " from asientos_contables_asientocontabledetalle a group by cuenta_id"
    print query

    asientos=select_all(query)

    for asiento in asientos:
        arbol = CuentasBalance()
        for cuenta in cuentas:
            if cuenta.id == asiento[0]:
                arbol.cuenta = cuenta
                arbol.debe = asiento[1]
                arbol.haber = asiento[2]
        arbol_list.append(arbol)
    lista_balance=arbol_list
    return render(request, 'balance/balance.html', {'cuentas': asientos_,'arbol_list':lista_balance})


def select_all(query):
    cursor=connection.cursor()
    cursor.execute(query)
    return cursor.fetchall()
