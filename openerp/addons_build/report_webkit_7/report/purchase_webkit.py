from openerp.report import report_sxw

class purchase_webkit_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(purchase_webkit_report, self).__init__(cr, uid, name, context=context)

report_sxw.report_sxw('report.purchase.rep.webkit','purchase.order','addons/report_webkit_7/report/purchase_rep_webkit.mako',parser=purchase_webkit_report) 

