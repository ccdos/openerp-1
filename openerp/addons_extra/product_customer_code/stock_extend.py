from openerp.osv import fields, osv

class stock_move(osv.osv):
    _inherit = "stock.move"
    _columns = {
         'product_customer_code': fields.char('Product customer code', size=64),
     }

