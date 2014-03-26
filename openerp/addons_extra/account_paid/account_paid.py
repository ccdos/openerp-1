from openerp.osv import fields, osv

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    def action_invoice_paid(self, cr, uid, ids, context=None):
        
       cr.execute('update account_invoice set residual=%s, state=%s where id=%s;',(0.0,'paid', ids[0]))
                     
        
       #self.pool.get('account.invoice').write(cr, uid, ids, { 
       #                            'residual': 0.0,
       #                            'state' : 'paid',
       #                           }, context=context)
       return True
    