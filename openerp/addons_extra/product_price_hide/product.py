from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class product_product(osv.osv):
    _inherit = "product.product"
    
    def _product_price(self, cr, uid, ids, name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        quantity = context.get('quantity') or 1.0
        pricelist = context.get('pricelist', False)
        partner = context.get('partner', False)
        if pricelist:
            # Support context pricelists specified as display_name or ID for compatibility
            if isinstance(pricelist, basestring):
                pricelist_ids = self.pool.get('product.pricelist').name_search(
                    cr, uid, pricelist, operator='=', context=context, limit=1)
                pricelist = pricelist_ids[0][0] if pricelist_ids else pricelist
            for id in ids:
                try:
                    price = self.pool.get('product.pricelist').price_get(cr,uid,[pricelist], id, quantity, partner=partner, context=context)[pricelist]
                except:
                    price = 0.0
                res[id] = price
        for id in ids:
            res.setdefault(id, 0.0)
        return res
    def _product_lst_price(self, cr, uid, ids, name, arg, context=None):
        res = {}
        product_uom_obj = self.pool.get('product.uom')
        for id in ids:
            res.setdefault(id, 0.0)
        for product in self.browse(cr, uid, ids, context=context):
            if 'uom' in context:
                uom = product.uos_id or product.uom_id
                res[product.id] = product_uom_obj._compute_price(cr, uid,
                        uom.id, product.list_price, context['uom'])
            else:
                res[product.id] = product.list_price
            res[product.id] =  (res[product.id] or 0.0) * (product.price_margin or 1.0) + product.price_extra
        return res
    _columns = {
       'lst_price' : fields.function(_product_lst_price, 
                                      read=['base.group_sale_manager'],   
                                      type='float', 
                                      string='Public Price', 
                                      digits_compute=dp.get_precision('Product Price')),
    }
product_product()
