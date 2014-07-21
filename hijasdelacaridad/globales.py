from django.db import connection

def execute_all_query(query):
    cursor=connection.cursor()
    cursor.execute(query)
    return cursor.fetchall()
