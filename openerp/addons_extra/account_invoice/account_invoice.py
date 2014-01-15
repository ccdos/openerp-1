from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    def _base(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = 0.0
            for line in invoice.invoice_line:
                res[invoice.id] += line.base
        return res
    
    _columns = {
                 'base_total': fields.function(_base, string='Base', type="float",
             digits_compute= dp.get_precision('Account'), store=True),
                }
    
    def compute_invoice_totals(self, cr, uid, inv, company_currency, ref, invoice_move_lines, context=None):
        if context is None:
            context={}
        total = 0
        total_currency = 0
        cur_obj = self.pool.get('res.currency')
        for i in invoice_move_lines:
            if inv.currency_id.id != company_currency:
                context.update({'date': inv.date_invoice or time.strftime('%Y-%m-%d')})
                i['currency_id'] = inv.currency_id.id
                i['amount_currency'] = i['price']
                i['price'] = cur_obj.compute(cr, uid, inv.currency_id.id,
                        company_currency, i['price'],
                        context=context)
            else:
                i['amount_currency'] = False
                i['currency_id'] = False
            i['ref'] = ref
            if inv.type in ('out_invoice','in_refund','out_refund'):
                total += i['price']
                total_currency += i['amount_currency'] or i['price']
                i['price'] = - i['price']
            else:
                total -= i['price']
                total_currency -= i['amount_currency'] or i['price']
        return total, total_currency, invoice_move_lines
    
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
account_invoice() 

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    def _base_line(self, cr, uid, ids, name, args, context=None):
        res = {}
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            price = line.price_unit * line.quantity
            res[line.id] = price
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res
    _columns = {
                 'base': fields.function(_base_line, string='Base', type="float",
             digits_compute= dp.get_precision('Account'), store=True),
                }
    
account_invoice_line()    
        
