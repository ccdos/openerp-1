from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class product_product(osv.osv):
    _inherit = "product.product"
    def _calculate_package_available(self, cr, uid, ids, name, args, context=None):
        res = {}
        for r in self.browse(cr, uid, ids, context=context):
            res[r.id] = float(r.qty_available /r.package_qty)
        return res
    def _calculate_package_virtual(self, cr, uid, ids, name, args, context=None):
        res = {}
        for r in self.browse(cr, uid, ids, context=context):
            res[r.id] = float(r.virtual_available /r.package_qty)
        return res
        
    _columns = {
                'package_qty': fields.float('Package Quantity', digits_compute= dp.get_precision('Stock Weight')),
                'package_qty_available': fields.function(_calculate_package_available, string = 'Package Available', digits_compute= dp.get_precision('Stock Weight')),
                'package_virtual_available': fields.function(_calculate_package_virtual, string = 'Package Virtual',digits_compute= dp.get_precision('Stock Weight')),                
                }
    
    _default = {
                'package_qty': '25.00',
                }