from django.db.models import Q
from django.utils.html import escape
from cuentas.models import Cuenta
from ajax_select import LookupChannel


class CuentaLookup(LookupChannel):
    model = Cuenta
    def get_query(self, q, request):
        print (request)
            
        return Cuenta.objects.filter(Q(cuenta__icontains=q) | Q(codigo__startswith=q), numchild=0).order_by('cuenta')

    def get_result(self, obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.cuenta

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        return u"<div>%s<div>%s</div></div>" % (escape(obj.cuenta), escape(obj.codigo))
        #return self.format_item_display(obj)

    def format_item_display(self, obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return u"<div> %s<div> %s</div> </div>" % (escape(obj.cuenta),escape(obj.codigo))
    
