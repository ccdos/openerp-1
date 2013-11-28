from openerp.osv import fields, osv

class delivery_carrier(osv.osv):
    _inherit = "delivery.carrier"
    _columns = {
        'product_id': fields.many2one('product.product', 'Delivery Product', required=False),
    }
