from openerp.osv import fields, osv


class product_template(osv.osv):
    _inherit = "product.template"

    _columns = {
        'supply_method': fields.selection([('produce', 'Manufacture'), ('buy', 'Buy'), ('produceExternal', 'Manufacture External')], 'Supply Method', required=True, help="Manufacture: When procuring the product, a manufacturing order or a task will be generated, depending on the product type. \nBuy: When procuring the product, a purchase order will be generated."),
    }
    
class procurement_order(osv.osv):
    _name = "procurement.order"
    _inherit = "procurement.order"
    def check_produce(self, cr, uid, ids, context=None):
            """ Checks product type.
            @return: True or False
            """
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            for procurement in self.browse(cr, uid, ids, context=context):
                product = procurement.product_id
                # TOFIX: if product type is 'service' but supply_method is 'buy'.
                if product.supply_method == 'buy':
                    return False
                if product.type == 'service':
                    res = self.check_produce_service(cr, uid, procurement, context)
                else:
                    res = self.check_produce_product(cr, uid, procurement, context)
                if not res:
                    return False
            return True
        
    def check_buy(self, cr, uid, ids, context=None):
            ''' return True if the supply method of the mto product is 'buy'
            '''
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            for procurement in self.browse(cr, uid, ids, context=context):
                if procurement.product_id.supply_method == 'produce':
                    return False
            return True
    def action_revert_done(self, cr, uid, ids, context=None):
        
        if not len(ids):
            return False
        for reg in self.browse(cr, uid, ids, context):
            if reg.state in ("confirmed","running"):
                self.write(cr, uid, [reg.id], {'state': 'draft'})
                return True
        return False