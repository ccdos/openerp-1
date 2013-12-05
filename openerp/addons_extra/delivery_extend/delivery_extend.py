from openerp.osv import fields, osv

class delivery_carrier(osv.osv):
    _inherit = "delivery.carrier"
    _columns = {
        'product_id': fields.many2one('product.product', 'Delivery Product', required=False),
    }
class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    def _prepare_shipping_invoice_line(self, cr, uid, picking, invoice, context=None):
        return None