from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from django.contrib.auth.models import User
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from hijasdelacaridad.globales import separador_de_miles
from comunidades.models import Comunidad
from ejercicios.models import Ejercicio
 
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from cuentas.models import Cuenta
from asientos_contables.views import AsientoContableDetalle
from hijasdelacaridad.globales import execute_all_query
from decimal import Decimal
from io import BytesIO
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4, cm,LEGAL, landscape,LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors

from reportlab.lib.enums import TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
from inventario.models import Categoria, CategoriaDetalle
 
# Register Fonts
#pdfmetrics.registerFont(TTFont('Arial', settings.STATIC_ROOT + 'fonts/arial.ttf'))
#pdfmetrics.registerFont(TTFont('Arial-Bold', settings.STATIC_ROOT + 'fonts/arialbd.ttf'))
 
# A large collection of style sheets pre-made for us
styles = getSampleStyleSheet()
# Our Custom Style
styles.add(ParagraphStyle(name='RightAlign', fontName='Arial', align=TA_RIGHT,fontSize=12))

width, height = A4
styles = getSampleStyleSheet()
styleN = styles["BodyText"]

styleBH = styles["BodyText"]
styleBH.fontSize=12
#styleBH.alignment = TA_CENTER
styleRIGTH=styles['Normal']
styleRIGTH.alignment=TA_RIGHT
styleRIGTH.font_size=12

def get_query_mayor(id_comunidad,codigo_menor,codigo_mayor):
    aux_menor=Cuenta(codigo=codigo_menor)
    aux_mayor=Cuenta(codigo=codigo_mayor)
    
    
    QUERY_MAYOR="with T AS (select c.id,c.cuenta, sum(ad.debe) as debe , sum(ad.haber) as haber, "\
    "sum(ad.debe)-sum(ad.haber)  as saldo,c.codigo,c.codigo_ordenado "\
    "from asientos_contables_asientocontabledetalle ad "\
    "join asientos_contables_asientocontable a on a.id = ad.asiento_contable_id "\
    "join cuentas_cuenta c on c.id = ad.cuenta_id "\
    "join comunidades_comunidad comu on comu.id = a.comunidad_id "\
    "join ejercicios_ejercicio e on e.anho = extract(year from a.fecha) "\
    "where comu.id = "+str(id_comunidad)+" and e.actual is True group by c.id, c.cuenta, c.tipo , "\
    " c.codigo_ordenado,c.codigo order by c.codigo_ordenado) "\
    "select c.codigo,c.cuenta, "\
    "(case when c.tipo like 'AC' then 'ACTIVO' "\
    "when c.tipo like 'PA' then 'PASIVO' "\
    "when c.tipo like 'IN' then 'INGRESO'"\
    "when c.tipo like 'EG' then 'EGRESO' "\
    "else c.tipo end ) as tipo,"\
    "(case when T.debe is null then 0 else T.debe end) as debe, "\
    "(case when T.haber is null then 0 else T.haber end) as haber, "\
    "(case when T.saldo is null then 0 else T.saldo end) as saldo,"\
    "(case when c.numchild > 0 then False else True end) as hijo from cuentas_cuenta c "\
    "full join T on T.id = c.id "\
    " where c.codigo_ordenado >= "+str(aux_menor.codigo_conversion())+" and "\
    " c.codigo_ordenado <= "+str(aux_mayor.codigo_conversion())+"  "\
    "order by c.codigo_ordenado "
    return QUERY_MAYOR


def some_view(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

        
       
    return response



def coord(x, y, unit=1):
    x, y = x * unit, height -  y * unit
    return x, y


def procesar(cuentas):
    # codigo - cuenta - tipo - debe - haber - saldo - hijo
    for cuenta in cuentas:
        if cuenta[6]: #si es hijo busca a los padres
            codigo = cuenta[0].split(".")
            buscar_padres(cuentas,cuenta[0],(".").join(codigo[0:len(codigo)-1]))
    return cuentas
            
def buscar_padres(cuentas,cuenta,papa):
    if papa != "":
        cuentas=sumar_al_padre(cuentas,cuenta,papa)
        codigo = papa.split(".")
        if codigo != "":
            buscar_padres(cuentas,papa,(".").join(codigo[0:len(codigo)-1]))
    return 

def sumar_al_padre(cuentas, cuenta, papa):
    hijo=get_cuenta_by_codigo(cuentas,cuenta)
    for cuenta in cuentas:
        if cuenta[0]== papa:
            cuenta[3]+=hijo[3]
            cuenta[4]+=hijo[4]
            cuenta[5]+=hijo[5]
    return cuentas
        

def get_cuenta_by_codigo(cuentas,codigo):
    for cuenta in cuentas:
        if cuenta[0] == codigo:
            return cuenta
    return None
    

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
 
class MyPrint:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize
 
    @staticmethod
    def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()
        # Header
        header = Paragraph('<B>HIJAS DE LA CARIDAD </B> ', styles['Normal'])
        
        w, h = header.wrap(doc.width, doc.topMargin)
        canvas.setFont("Helvetica", 9)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin +10)
        
        # Footer
        footer = Paragraph('' , styles['Normal'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h-40)
 
        # Release the canvas
        canvas.restoreState()
        
    def print_mayor(self,cuentas,comunidad):
        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                rightMargin=50,
                                leftMargin=50,
                                topMargin=50,
                                bottomMargin=50,
                                pagesize=self.pagesize,
                                )
        # Our container for 'Flowable' objects
        elements = [] 
        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        #styles.add(ParagraphStyle(name='RightAlign', fontName='Arial', alignment=TA_RIGHT))
        hcodigo = Paragraph('''<b>Cod.</b>''', styleBH)
        hcuenta = Paragraph('''<b>Cuenta.</b>''', styleBH)
        hdebe = Paragraph('''<b>Debe</b>''', styleBH)
        hhaber = Paragraph('''<b>Haber</b>''', styleBH)
        hsaldo = Paragraph('''<b>Saldo</b>''', styleBH)
            
        data = [[hcodigo, hcuenta, hdebe, hhaber,hsaldo]]
        cont=0
        
        for cuenta in cuentas:
            if cuenta[6]:
                array = [cuenta[0], (cuenta[1]), 
                        Paragraph(separador_de_miles(str(cuenta[3])),styleRIGTH),Paragraph(str(cuenta[4]),styleRIGTH),
                        Paragraph(str(cuenta[5]),styleRIGTH)]
            else:
                array = [Paragraph("<b>"+cuenta[0]+"</b>",styleN),Paragraph("<b>"+cuenta[1]+"</b>",styleN),
                         Paragraph(separador_de_miles(cuenta[3]),styleRIGTH),Paragraph(separador_de_miles(cuenta[4]),styleRIGTH),
                         Paragraph(separador_de_miles(cuenta[5]),styleRIGTH)]
            data.append(array)
                    # Create the table
        table = Table(data, colWidths=[1.8 * cm, 8.2 * cm, 2.7* cm, 2.7 * cm, 2.7 * cm], )
        
        table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                       ('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))
        
        libro_mayor=Table([['',Paragraph('<b>LIBRO MAYOR - '+comunidad+' </b>', styleBH),''],['','','']],
                          colWidths=[1 * cm, 14 * cm,1*cm ]
                          )
      
        elements.append(libro_mayor)
        elements.append(table)
        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer,
                  canvasmaker=NumberedCanvas)
 
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def print_mayor_detalle(self,cuentas,comunidad,asientos):
        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                rightMargin=50,
                                leftMargin=50,
                                topMargin=50,
                                bottomMargin=50,
                                pagesize=self.pagesize,
                                )
        # Our container for 'Flowable' objects
        elements = [] 
        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        #styles.add(ParagraphStyle(name='RightAlign', fontName='Arial', alignment=TA_RIGHT))
        hfecha = Paragraph('''<b>Fecha.</b>''', styleBH)
        hdebe = Paragraph('''<b>Debe</b>''', styleBH)
        hhaber = Paragraph('''<b>Haber</b>''', styleBH)
        hsaldo = Paragraph('''<b>Saldo</b>''', styleBH)
        hconcepto = Paragraph('''<b>Concepto</b>''', styleBH)
        t_head=[hfecha, hdebe, hhaber,hsaldo,hconcepto]
        t_widths=[2.3 * cm, 2.7 * cm, 2.7* cm, 2.7 * cm, 6 * cm]
        data=[]
        
        libro_mayor=Table([['',Paragraph('<b>LIBRO MAYOR DETALLADO - '+comunidad+' </b>', styleBH),'']],
                          colWidths=[1 * cm, 14 * cm,1*cm ]
                          )
        
        elements.append(libro_mayor)
        for cuenta in cuentas:
            cont=True
            for asiento in asientos:
                if cuenta[0] == asiento.cuenta_id:
                   if cont:
                       cont=False
                       cuenta_table=Table([['','',''],
                                            ['',Paragraph(cuenta[3]+" - "+cuenta[1]+" : "+str(cuenta[2]), styleBH),''],
                                            ],
                              colWidths=[1 * cm, 14 * cm,1*cm ]
                              )
                       data=[]
                       elements.append(cuenta_table)
                       data.append(t_head)
                   array=[asiento.asiento_contable.fecha,Paragraph(separador_de_miles(asiento.debe),styleRIGTH),
                           Paragraph(separador_de_miles(asiento.haber),styleRIGTH), 
                           Paragraph(separador_de_miles(asiento.saldo()), styleRIGTH),
                                     asiento.observacion]
                   data.append(array)
            table = Table(data, colWidths=t_widths )
            table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))
            elements.append(table)
           
        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer,
                  canvasmaker=NumberedCanvas)
 
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
    
    def print_inventario_general(self,categorias,comunidades,detalles):
        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                rightMargin=50,
                                leftMargin=50,
                                topMargin=50,
                                bottomMargin=50,
                                pagesize=self.pagesize,
                                )
        # Our container for 'Flowable' objects
        elements = []
        for comunidad in comunidades:
            print comunidad.comunidad
            inventario=Table([['',Paragraph('<b>INVENTARIO - '+comunidad.comunidad+' </b>', styleBH),''],['','','']],
                              colWidths=[1 * cm, 14 * cm,1*cm ]
                              )
            elements.append(inventario)
     
            # A large collection of style sheets pre-made for us
            styles = getSampleStyleSheet()
            t_widths=[7 * cm, 2.7 * cm, 2.7* cm, 2.7 * cm]
            
            data=[[Paragraph('<b>Descripcion</b>', styleBH),
                  Paragraph('<b>Cantidad</b>', styleBH),
                  Paragraph('<b>Total</b>', styleBH)
                  ]]
            
            for c in categorias:
                array=[c.nombre,Paragraph(separador_de_miles(c.cantidad(comunidad.id)),styleRIGTH),Paragraph(separador_de_miles(c.total(comunidad.id)),styleRIGTH)]
                data.append(array)
            categoria_table=Table(data,colWidths=t_widths)    
            categoria_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                               ('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))
            elements.append(categoria_table)
            
                    
            hdescripcion = Paragraph('''<b>Descripcion.</b>''', styleBH)
            hcantidad = Paragraph('''<b>Cantidad</b>''', styleBH)
            hprecio = Paragraph('''<b>Precio Unitario</b>''', styleBH)
            htotal = Paragraph('''<b>Total</b>''', styleBH)
    
            t_head=[hdescripcion, hcantidad, hprecio,htotal]
            
            
            
            for categoria in categorias:
                categoria_table=Table([['','',''],
                                                ['',Paragraph(categoria.nombre,styleBH),''],
                                                ], colWidths=[1 * cm, 14 * cm,1*cm ]
                                  )
                elements.append(categoria_table)
                data=[t_head]
                
                for detalle in detalles:
                    if detalle.categoria_id == categoria.id:
                        array=[detalle.descripcion,Paragraph(separador_de_miles(detalle.cantidad),styleRIGTH),
                               Paragraph(separador_de_miles(detalle.precio_unitario),styleRIGTH), 
                               Paragraph(separador_de_miles(detalle.precio_total()), styleRIGTH),]
                        data.append(array)
                           
                table = Table(data, colWidths=t_widths )
                table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                               ('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))
                elements.append(table)
                        
    
        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer,
                  canvasmaker=NumberedCanvas)
 
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
    
    def print_inventario_comunidad(self,categorias,comunidad,detalles):
        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                rightMargin=50,
                                leftMargin=50,
                                topMargin=50,
                                bottomMargin=50,
                                pagesize=self.pagesize,
                                )
        # Our container for 'Flowable' objects
        elements = []
        inventario=Table([['',Paragraph('<b>INVENTARIO - '+comunidad.comunidad+' </b>', styleBH),''],['','','']],
                          colWidths=[1 * cm, 14 * cm,1*cm ]
                          )
        elements.append(inventario)
 
        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        t_widths=[7 * cm, 2.7 * cm, 2.7* cm, 2.7 * cm]
        
        data=[[Paragraph('<b>Descripcion</b>', styleBH),
              Paragraph('<b>Cantidad</b>', styleBH),
              Paragraph('<b>Total</b>', styleBH)
              ]]
        
        for c in categorias:
            array=[c.nombre,Paragraph(separador_de_miles(c.cantidad(comunidad.id)),styleRIGTH),Paragraph(separador_de_miles(c.total(comunidad.id)),styleRIGTH)]
            data.append(array)
        categoria_table=Table(data,colWidths=t_widths)    
        categoria_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))
        elements.append(categoria_table)
        
                
        hdescripcion = Paragraph('''<b>Descripcion.</b>''', styleBH)
        hcantidad = Paragraph('''<b>Cantidad</b>''', styleBH)
        hprecio = Paragraph('''<b>Precio Unitario</b>''', styleBH)
        htotal = Paragraph('''<b>Total</b>''', styleBH)

        t_head=[hdescripcion, hcantidad, hprecio,htotal]
        
        data=[]
        
        for categoria in categorias:
            categoria_table=Table([['','',''],
                                            ['',Paragraph(categoria.nombre,styleBH),''],
                                            ], colWidths=[1 * cm, 14 * cm,1*cm ]
                              )
            elements.append(categoria_table)
            data=[t_head]
            
            for detalle in detalles:
                if detalle.categoria_id == categoria.id:
                    array=[detalle.descripcion,Paragraph(separador_de_miles(detalle.cantidad),styleRIGTH),
                           Paragraph(separador_de_miles(detalle.precio_unitario),styleRIGTH), 
                           Paragraph(separador_de_miles(detalle.precio_total()), styleRIGTH),]
                    data.append(array)
                       
            table = Table(data, colWidths=t_widths )
            table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))
            elements.append(table)
                    
    
        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer,
                  canvasmaker=NumberedCanvas)
 
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        return pdf


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be
        self.setFont("Helvetica", 9)
        self.drawRightString(190 * mm, 15 * mm + (0.05 * inch),
                             "Pag. %d de %d" % (self._pageNumber, page_count))
            
            
            
def mayor(request,id_comunidad,desde,hasta):
    comunidad=Comunidad.objects.get(pk=id_comunidad)
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Libro Mayor - '+comunidad.comunidad+'.pdf"'
 
    buffer = BytesIO()
 
    report = MyPrint(buffer, 'A4')
    
    mayor=execute_all_query(get_query_mayor(id_comunidad, desde,hasta))
    lista=[]
        
    for m in mayor:
       aux=[m[0],m[1],m[2],m[3],m[4],m[5],m[6]]
       lista.append(aux)
        
    cuentas=procesar(lista)
    
    pdf = report.print_mayor(cuentas,comunidad.comunidad)
 
    response.write(pdf)
    return response

def mayor_detalle(request,id_comunidad,desde,hasta):
    comunidad=Comunidad.objects.get(pk=id_comunidad)
     # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Libro Mayor Detallado - '+comunidad.comunidad+'.pdf"'
 
    buffer = BytesIO()
 
    report = MyPrint(buffer, 'A4')
    
    ejercicio_anho = Ejercicio.objects.get(actual=True).anho
    aux_menor=Cuenta(codigo=desde)
    aux_mayor=Cuenta(codigo=hasta)
    
    query = " select distinct c.id,c.cuenta,c.codigo,c.codigo_ordenado from cuentas_cuenta c " \
            " join asientos_contables_asientocontabledetalle ad on ad.cuenta_id = c.id " \
            " join asientos_contables_asientocontable a on a.id=ad.asiento_contable_id " \
            " join ejercicios_ejercicio e on e.anho = extract(year from a.fecha) "\
            " where a.comunidad_id=" + str(id_comunidad) +"  and extract( year from a.fecha) ="+str(ejercicio_anho)+" "\
            " and c.codigo_ordenado >= "+str(aux_menor.codigo_conversion())+" and "\
            " c.codigo_ordenado <= "+str(aux_mayor.codigo_conversion())+"  "\
            " order by c.codigo_ordenado"
            
    cuentas_list = execute_all_query(query)
    asientos=AsientoContableDetalle.objects.filter(asiento_contable__fecha__year=ejercicio_anho,asiento_contable__comunidad_id=id_comunidad).order_by('cuenta__codigo_ordenado')
    cuentas=[]
    for id_cuenta,cuenta,codigo,aux in cuentas_list:
        debe=haber=0
        for asiento in asientos:
            if id_cuenta ==  asiento.cuenta_id:
                debe+=asiento.debe
                haber+=asiento.haber
        cuentas.append([id_cuenta,cuenta,debe-haber,codigo])
    for cuenta in cuentas:
        print cuenta
        
    pdf = report.print_mayor_detalle(cuentas,comunidad.comunidad,asientos)
    response.write(pdf)
    
    return response

def inventario_comunidad(request,id_comunidad):
    comunidad=Comunidad.objects.get(pk=id_comunidad)
     # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Libro Inventario - '+comunidad.comunidad+'.pdf"'
 
    buffer = BytesIO()
 
    report = MyPrint(buffer, 'A4')
    categorias=Categoria.objects.all()
    detalles=CategoriaDetalle.objects.filter(comunidad_id=id_comunidad)
    
    pdf = report.print_inventario_comunidad(categorias,comunidad,detalles)
    
    response.write(pdf)
    
    return response
        
def inventario_general(request):
     # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Inventario todas las comunidades.pdf"'
 
    buffer = BytesIO()
 
    report = MyPrint(buffer, 'A4')
    categorias=Categoria.objects.all()
    detalles=CategoriaDetalle.objects.all()
    comunidades=Comunidad.objects.all()
    
    pdf = report.print_inventario_general(categorias,comunidades,detalles)
    response.write(pdf)
    
    return response
