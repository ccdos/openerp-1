
from openerp.osv import fields, osv

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def invoice_print(self, cr, uid, ids, context=None):
            '''
            This function prints the invoice and mark it as sent, so that we can see more easily the next step of the workflow
            '''
            assert len(ids) == 1, 'This option should only be used for a single id at a time.'
            self.write(cr, uid, ids, {'sent': True}, context=context)
            datas = {
                 'ids': ids,
                 'model': 'account.invoice',
                 'form': self.read(cr, uid, ids[0], context=context)
            }
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.account_invoice',
                'datas': datas,
                'nodestroy' : True
            }