from cuentas.models import Cuenta

def cuentas_custom(request):
    cuentas=Cuenta.objects.all()
    for c in cuentas:
        c.path=crear_path(c.codigo)
        c.numchild=numchild_(c)
        c.depth=prof(c.codigo)
        c.codigo_ordenado=c.codigo_conversion()
        c.tipo=c.cargar_tipo()
        c.permiso_debe=True
        c.permiso_haber=True
        c.numchild=numchild_(c)
        c.save()
        
    for c in cuentas:
         c.numchild=numchild_(c)
         c.save()
    return render(request, 'admin/index.html')
def crear_path(codigo):
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    longitud=len(codigo.split("."))
    nros=codigo.split(".")
    ceros='000'
    path=""
    for i in range(longitud):
        path+=ceros+alphabet[int(nros[i])]
    return path

def prof(codigo):
    return len(codigo.split("."))
def numchild_(c):
    return Cuenta.objects.filter(codigo__startswith=c.codigo,depth=c.depth+1).count()
  