from openerp.osv import fields, orm


class stock_move(orm.Model):
    _inherit = "stock.move"

    _columns = {
        'invoice_line_id': fields.many2one(
            'account.invoice.line', 'Invoice line', readonly=True),
    }


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    _columns = {
        'invoice_id': fields.many2one(
            'account.invoice', 'Invoice', readonly=True),
    }

    def _invoice_hook(self, cr, uid, picking, invoice_id):
        res = super(stock_picking, self)._invoice_hook(
            cr, uid, picking, invoice_id)
        picking.write({'invoice_id': invoice_id})
        return res

    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        res = super(stock_picking, self)._invoice_line_hook(
            cr, uid, move_line, invoice_line_id)
        move_line.write({'invoice_line_id': invoice_line_id})
        return res


class stock_picking_out(orm.Model):
    _inherit = "stock.picking.out"

    _columns = {
        'invoice_id': fields.many2one(
            'account.invoice', 'Invoice', readonly=True),
    }


class stock_picking_in(orm.Model):
    _inherit = "stock.picking.in"

    _columns = {
        'invoice_id': fields.many2one(
            'account.invoice', 'Invoice', readonly=True),
    }


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    _columns = {
        'picking_ids': fields.one2many(
            'stock.picking', 'invoice_id', 'Related Pickings', readonly=True,
            help="Related pickings (only when the invoice has been generated from the picking)."),
    }


class account_invoice_line(orm.Model):
    _inherit = "account.invoice.line"

    _columns = {
        'move_line_ids': fields.one2many(
            'stock.move', 'invoice_line_id', 'Related Stock Moves',
            readonly=True,
            help="Related stock moves (only when the invoice has been generated from the picking)."),
        }
