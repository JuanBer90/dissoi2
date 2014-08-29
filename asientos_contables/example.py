#!/usr/bin/env python
#coding: utf8
from io import BytesIO
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, cm,LEGAL, landscape,LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from django.http.response import HttpResponse
from demo_project.demo_app.constantes import execute_query, execute_all_query
from demo_project.demo_app.models import Envio, EnvioProducto, Cliente, Distribuidor

width, height = LEGAL
styles = getSampleStyleSheet()
styleN = styles["BodyText"]
styleN.alignment = TA_LEFT
styleBH = styles["BodyText"]
styleBH.alignment = TA_CENTER
styleRIGTH=styles['Normal']
styleRIGTH.alignment=TA_RIGHT


def some_view(request,id):
    envio=Envio.objects.get(pk=id)
    if envio.distribuidor_id == None:
        query_cliente="select c.nombre from cliente c join envio_producto ep on ep.cliente_id = c.id_cliente "\
        " join envio e on e.id_envio = ep.envio_id where e.id_envio="+str(id)
        cliente_nombre=execute_query(query_cliente)[0]
    else:
        cliente_nombre=Distribuidor.objects.get(pk=envio.distribuidor_id).nombre

    query_ep="select count(*),p.codigo,ep.lote, p.nombre,p.precio from envio_producto ep"\
    " join producto p on p.id_producto = ep.producto_id where ep.envio_id= "+str(id)+""\
    " group by p.codigo,ep.lote,p.nombre, p.precio"

    envios_productos=execute_all_query(query_ep)
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Nota de Envio Nro. '+str(envio.nro_talonario)+'.pdf"'

    buffer = BytesIO()

    # Create the PDF object, using the BytesIO object as its "file."

    p = canvas.Canvas(buffer,pagesize=A4)

    encabezado(p,envio.nro_talonario)
    cuerpo(p=p,envio=envio,envios_productos=envios_productos,cliente_nombre=cliente_nombre)
    encabezado(canvas=p, nro=envio.nro_talonario, copia=True)
    cuerpo(p=p, envio=envio, envios_productos=envios_productos, copia=True, cliente_nombre=cliente_nombre)
    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def coord(x, y, unit=1):
    x, y = x * unit, height -  y * unit
    return x, y

def encabezado(canvas,nro,copia=False):
     from reportlab.lib.colors import white, darkblue,black
     x=740

     canvas.setFillColor(darkblue)
     canvas.rect(30,x,85,60,fill=True,stroke=False)

     canvas.setFillColor(white)
     canvas.setStrokeColor(white)
     canvas.setFont("Helvetica-Bold", 35)
     canvas.drawString(40, x+25, "MIS")

     canvas.setFillColor(white)
     canvas.setStrokeColor(white)
     canvas.setFont("Helvetica-Bold", 12)
     canvas.drawString(37,x+10, "PARAGUAY")

     canvas.setFillColor(black)
     canvas.setStrokeColor(black)
     canvas.setFont("Helvetica-Bold", 11)
     canvas.drawString(130, x+47, "MIS Implants Paraguay")
     canvas.drawString(130, x+31, "América 192 c/ Mcal. López")
     canvas.drawString(130, x+15, "Tel.: +59521 21 213193")
     canvas.drawString(130, x+2, "www.misimplants.com.py")

     canvas.setFont("Helvetica-Bold", 18)
     canvas.drawString(350, x+17, "Nro. "+str(nro))


def coords(canvas):
    from reportlab.lib.units import inch,mm
    from reportlab.lib.colors import pink, black, red, blue, green
    c = canvas
    c.setStrokeColor(black)
    c.grid([inch, 2*inch, 3*inch, 4*inch],
           [0.5*inch, inch, 1.5*inch, 2*inch, 2.5*inch])
    rows = [["Header1", "Header2"], ["Data1", "Data2"]]

def cuerpo(p,envio,envios_productos,cliente_nombre,copia=False):
    # Headers
    fecha = "<b>Fecha: </b>  " + str(envio.fecha_envio)

    hnotaenvio = Paragraph('''<b>NOTA DE ENVIO</b>''', styleBH)
    hfecha = Paragraph('' + fecha + '', styleN)
    hcantidad = Paragraph('''<b>Cant.</b>''', styleBH)
    hcodigo = Paragraph('''<b>Código</b>''', styleBH)
    hlote = Paragraph('''<b>Lote</b>''', styleBH)
    hdescripcion = Paragraph('''<b>Descripción</b>''', styleBH)
    hprecio = Paragraph('''<b>Precio</b>''', styleBH)

    data = [[hnotaenvio, '', '', hfecha, ''],
            [Paragraph('''<b>Para:</b>''', styleBH), str(cliente_nombre), '', '', ''],
            [hcantidad, hcodigo, hlote, hdescripcion, hprecio]]
    for ep in envios_productos:
        array = [Paragraph('' + str(ep[0]) + '', styleRIGTH), str(ep[1]), str(ep[2]),
                 str(ep[3]), Paragraph('' + str(ep[4]) + '', styleRIGTH)]
        data.append(array)

    declaracion = "Declaración:\n" \
                  "1- Acuso recibo de los productos detallados arriba los cuales son ______ a abonar" \
                  " o devolverlos a MIS Implantes Paraguay,\n en el plazo máximo de 7 días.\n" \
                  "2- Los productos que cumplan un plazo de 30 días en ________________ correspondiente tendrán un recargo en " \
                  "su valor\n del 10% de forma automática."

    data.append([declaracion, '', '', '', '', ])
    table = Table(data, colWidths=[1.8 * cm, 2.5 * cm, 2.5 * cm, 8 * cm, 3 * cm], )

    table.setStyle(TableStyle([
        ('SPAN', (0, 0), (2, 0)),
        ('SPAN', (0, len(data) - 1), (4, len(data) - 1)),
        ('FONTSIZE', (0, len(data) - 1), (4, len(data) - 1), 8),
        ('SPAN', (1, 1), (4, 1)),
        ('SPAN', (3, 0), (4, 0)),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    table.wrapOn(p, width, height)
    table.drawOn(p, *coord(1.8, 16, cm))

    ''' FIRMA Y ACLARACION DEL CLIENTE '''

    data2 = [['FIRMA:', ''], ['Aclaración', ''], ['C.I. Nro.', '']]
    table2 = Table(data2, colWidths=[2 * cm, 5 * cm])
    table2.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    table2.wrapOn(p, width, height)
    table2.drawOn(p, *coord(1.8, 32, cm))

    ''' CONTROL DE SALIDA DE MERCADERIAS '''
    control_salida = [[Paragraph('''Control de Salida:''', styleBH), ''], ['Firma Vendedor:', ''],
                      ['Firma Administración:', '']]
    table3 = Table(control_salida, colWidths=[4 * cm, 5 * cm])
    table3.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    table3.wrapOn(p, width, height)
    table3.drawOn(p, *coord(10, 32, cm))

    p.showPage()
    p.save()
