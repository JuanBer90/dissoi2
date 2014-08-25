from django.db.models import Q
from django.utils.html import escape
from comunidades.models import Comunidad
from ajax_select import LookupChannel


class ComunidadLookup(LookupChannel):
    model = Comunidad
    def get_query(self, q, request):
        return Comunidad.objects.filter(Q(comunidad__istartswith=q)).order_by('comunidad')
        
    def get_result(self, obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.comunidad

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        return u"<div>%s<div><b>%s</b></div></div>" % (escape(obj.comunidad), escape(obj.pais.pais))
        #return self.format_item_display(obj)

    def format_item_display(self, obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return u"<div> %s<div><b> %s </b></div> </div>" % (escape(obj.comunidad),escape(obj.pais.pais))
    
    
    
