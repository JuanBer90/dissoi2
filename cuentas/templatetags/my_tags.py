from decimal import Decimal
from django import template

#Django template custom math filters
#Ref : https://code.djangoproject.com/ticket/361
from cuentas.models import TIPOS_DE_CUENTA

register = template.Library()

def mult(value, arg):
    "Multiplies the arg and the value"
    return int(value) * int(arg)

def sub(value, arg):
    "Subtracts the arg from the value"
    return int(value) - int(arg)

def div(value, arg):
    "Divides the value by the arg"
    return int(value) / int(arg)

def espacios(value):
    string="text-indent: "
    total=0
    for i in range(value-1):
        total+=3
    string+=str(total)+"em;"
    return string

register.filter('espacios', espacios)
register.filter('mult', mult)
register.filter('sub', sub)
register.filter('div', div)

