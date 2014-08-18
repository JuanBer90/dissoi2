from decimal import Decimal
from django import template

#Django template custom math filters
#Ref : https://code.djangoproject.com/ticket/361
from django.shortcuts import render
from django.template.base import Node
from cuentas.models import TIPOS_DE_CUENTA, Cuenta
from cuentas_bancarias.models import CuentaBancaria

register = template.Library()

def mult(value, arg):
    "Multiplies the arg and the value"
    return int(value) * int(arg)

def sub(value, arg):
    "Subtracts the arg from the value"
    return int(value) - int(arg)

def sum(value, arg):
    "Subtracts the arg from the value"
    return int(value) + int(arg)


def div(value, arg):
    "Divides the value by the arg"
    return int(value) / int(arg)

def saldo_anterior(value, index):
    saldo=value[index].saldo()
    while index > 0 and value[index-1].cuenta_id == value[index].cuenta_id:
         saldo+=value[index-1].saldo()
         index -= 1
    return saldo

def espacios(value):
    string="text-indent: "
    total=0
    for i in range(value-1):
        total+=3
    string+=str(total)+"em;"
    return string

class BancoId(Node):
    def render(self, context):
        return Cuenta.objects.filter(codigo='1.2.5.2')[0].id

def banco_codigo(parser, token):
    return BancoId()

def to_int(value):
    return int(value)

register.filter('to_int', to_int)
register.filter('saldo_anterior', saldo_anterior)
register.filter('espacios', espacios)
register.filter('mult', mult)
register.filter('sub', sub)
register.filter('sum', sum)
register.filter('div', div)
register.tag('banco_codigo',banco_codigo)