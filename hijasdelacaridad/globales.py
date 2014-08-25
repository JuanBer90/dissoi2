from django.db import connection
from decimal import Decimal

def execute_all_query(query):
    cursor=connection.cursor()
    cursor.execute(query)
    return cursor.fetchall()


def separador_de_miles(numero):
   numero=str(numero)
   vector=numero.split(".")
   s=vector[0]
   for i in range(len(vector[0]),0,-3):
       s=s[:i]+"."+s[i:]
   a=s[:len(s)-1]
   if len(vector) == 2:
    a+= ","+vector[1]
   return a
   
