from openerp.osv import fields, osv, orm
from openerp import pooler
from openerp.tools.translate import _


class account_move_line(osv.osv):
    _inherit = "account.move.line"
    #accumulated_global = 0
    #accumulateds = {}
    
    def _update_check(self, cr, uid, ids, context=None):
        done = {}
        for line in self.browse(cr, uid, ids, context=context):
            err_msg = _('Move name (id): %s (%s)') % (line.move_id.name, str(line.move_id.id))
            if line.move_id.state <> 'draft' and (not line.journal_id.entry_posted):
                raise osv.except_osv(_('Error!'), _('You cannot do this modification on a confirmed entry. You can just change some non legal fields or you must unconfirm the journal entry first.\n%s.') % err_msg)
            #if line.reconcile_id:
            #    raise osv.except_osv(_('Error!'), _('You cannot do this modification on a reconciled entry. You can just change some non legal fields or you must unreconcile first.\n%s.') % err_msg)
            t = (line.journal_id.id, line.period_id.id)
            if t not in done:
                self._update_journal_check(cr, uid, line.journal_id.id, line.period_id.id, context)
                done[t] = True
        return True
        
    def _get_accumulated(self, cr, uid, ids,name, unknow_none, context=None):
        res = dict.fromkeys(ids, False)
        #accumulated = self.accumulated_global
        lines = self.browse(cr, uid, ids, context=context)
        #line0 = lines[0]
        #self.accumulateds[line0.id] = [line0.debit-line0.credit,line0.date]
        accumulated = 0
        for line in lines:
            debit = line.debit
            credit = line.credit
            accumulated += debit - credit
            res[line.id] = accumulated
        return res
    
    def _get_balance(self, cr, uid, ids,name, unknow_none, context=None):
        res = dict.fromkeys(ids, False)
        for line in self.browse(cr, uid, ids, context=context):
            debit = line.debit
            credit = line.credit
            res[line.id] = debit - credit
        return res
    
    _columns = {
                'balance': fields.function(_get_balance, type='float',digits=(16,2), string='Balance'),
                'accumulated': fields.function(_get_accumulated, type='float', digits=(16,2), string='accumulated'),
                'notes': fields.char('notes',size=128),
                }
    _order = "date, id"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        limit = 500
        return super(account_move_line, self).search(cr, uid, args, offset, limit, order, context, count)
    
    def list_accounts(self, cr, uid, context=None):
        ids = self.pool.get('account.account').search(cr,uid,[],0, None,('code'))
        lines = self.pool.get('account.account').browse(cr, uid, ids, context)
        res = []
        for line in lines:
            length  = 9 - len(line.code.strip())
            spaces = '&nbsp;' * length *2 + '&nbsp;'
            description = line.code + spaces + line.name
            res.append((line.id,description,line.code))
        #names = self.pool.get('account.account').name_get(cr, uid, ids, context)
        return res
    
    #def print_extract(self, cr, uid, context=None):
        #win_obj = self.pool.get('ir.actions.act_window')
        #res = win_obj.for_xml_id(cr, uid, 'account', 'account_report_general_ledger_view', context)
        #return res
        

    
account_move_line()