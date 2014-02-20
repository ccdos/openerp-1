from openerp.osv import fields, osv
from openerp import netsvc
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import  DEFAULT_SERVER_DATETIME_FORMAT

class product_template(osv.osv):
    _inherit = "product.template"

    _columns = {
        'supply_method': fields.selection([('produce', 'Manufacture'), ('buy', 'Buy'), ('produceExternal', 'Manufacture External')], 'Supply Method', required=True, help="Manufacture: When procuring the product, a manufacturing order or a task will be generated, depending on the product type. \nBuy: When procuring the product, a purchase order will be generated."),
    }
    
class procurement_order(osv.osv):
    _inherit = "procurement.order"
    _columns ={
               'date_order': fields.datetime('Order date', required=True, select=True),
               }
    _defaults ={
               'location_id':7,
               }
    
    def _get_purchase_order_date(self, cr, uid, procurement, company, schedule_date, context=None):
        """Return the datetime value to use as Order Date (``date_order``) for the
           Purchase Order created to satisfy the given procurement.

           :param browse_record procurement: the procurement for which a PO will be created.
           :param browse_report company: the company to which the new PO will belong to.
           :param datetime schedule_date: desired Scheduled Date for the Purchase Order lines.
           :rtype: datetime
           :return: the desired Order Date for the PO
        """
        date = procurement.date_order
        if date == False:
            date = str(schedule_date)
        procurement_date_order = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
        schedule_date = (procurement_date_order - relativedelta(days=company.po_lead))
        return schedule_date    
    
    def check_produce(self, cr, uid, ids, context=None):
        """ Checks product type.
        @return: True or False
        """
        
        sale_mov_obj = self.pool.get('sale.order')                
        ids_sales = sale_mov_obj.search(cr,uid,[],0, None)
        
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
            
            for line in sale_mov_obj.browse(cr, uid, ids_sales):
                origin = line.name
                if origin == procurement.origin:
                    if line.state == 'procurement':
                        line.write({'state': 'procurement_production'})
                    else:
                        line.write({'state': 'procurement_all'})
                    
            
        return True
        
    def check_buy(self, cr, uid, ids, context=None):
            ''' return True if the supply method of the mto product is 'buy'
            '''
            sale_mov_obj = self.pool.get('sale.order')                
            ids_sales = sale_mov_obj.search(cr,uid,[],0, None)
        
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            for procurement in self.browse(cr, uid, ids, context=context):
                if procurement.product_id.supply_method == 'produce':
                    return False
            for line in sale_mov_obj.browse(cr, uid, ids_sales):
                origin = line.name
                if origin == procurement.origin:
                    if line.state == 'procurement':
                        line.write({'state': 'procurement_purchase'})
                    else:
                        line.write({'state': 'procurement_all'})
            return True
    def action_revert_done(self, cr, uid, ids, context=None):
        
        if not len(ids):
            return False
        for reg in self.browse(cr, uid, ids, context):
            if reg.state in ("confirmed","running"):
                self.write(cr, uid, [reg.id], {'state': 'draft'})
                return True
        return False
 
        
procurement_order()

class make_procurement(osv.osv_memory):
    _inherit = 'make.procurement'
    
    def make_procurement(self, cr, uid, ids, context=None):
        """ Creates procurement order for selected product.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return: A dictionary which loads Procurement form view.
        """
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context).login
        wh_obj = self.pool.get('stock.warehouse')
        procurement_obj = self.pool.get('procurement.order')
        wf_service = netsvc.LocalService("workflow")
        data_obj = self.pool.get('ir.model.data')
        product_obj = self.pool.get('product.template')
        
        for proc in self.browse(cr, uid, ids, context=context):
            wh = wh_obj.browse(cr, uid, proc.warehouse_id.id, context=context)
            product_id = proc.uom_id.id
            product_obj = product_obj.browse(cr, uid, product_id, context=context)
            procure_id = procurement_obj.create(cr, uid, {
                'name':'INT: '+str(user),
                'date_planned': proc.date_planned,
                'product_id': proc.product_id.id,
                'product_qty': proc.qty,
                'product_uom': proc.uom_id.id,
                #'location_id': wh.lot_stock_id.id,
                'location_id': product_obj.property_stock_production.id,
                'procure_method':'make_to_order',
            })
    
            wf_service.trg_validate(uid, 'procurement.order', procure_id, 'button_confirm', cr)
    
    
        id2 = data_obj._get_id(cr, uid, 'procurement', 'procurement_tree_view')
        id3 = data_obj._get_id(cr, uid, 'procurement', 'procurement_form_view')
    
        if id2:
            id2 = data_obj.browse(cr, uid, id2, context=context).res_id
        if id3:
            id3 = data_obj.browse(cr, uid, id3, context=context).res_id
    
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'procurement.order',
            'res_id' : procure_id,
            'views': [(id3,'form'),(id2,'tree')],
            'type': 'ir.actions.act_window',
         }