from django.db import connection
from decimal import Decimal

USUARIO_LIMITADO="usuarios.limitado"
def execute_all_query(query):
    cursor=connection.cursor()
    cursor.execute(query)
    return cursor.fetchall()


def separador_de_miles(numero):
   numero=str(numero)
   vector=numero.split(".")
   s=vector[0]
   for i in range(len(vector[0]),0,-3):
      if i == 1 and s[0] == "-":
           s=s[:i]+s[i:]
      else:
        s=s[:i]+"."+s[i:]
   a=s[:len(s)-1]
   if len(vector) == 2:
    a+= ","+vector[1]
   return a
   
def get_comunidad(usuario):
    id=0
    aux=Usuario.objects.filter(user_id=usuario.id).count()   
    if aux >0:
       id=Usuario.objects.get(user_id=usuario.id).comunidad_id
    return id
