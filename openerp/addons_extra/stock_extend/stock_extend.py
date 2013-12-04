from openerp.osv import fields, osv

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {
                'seals_first' : fields.integer('Seal first'),
                'seals_last' : fields.integer('Seal last'),  
                'tare' : fields.float('tare'),      
                'weight_manual' : fields.float('weight'), 
                'weight_net_manual' : fields.float('weight net'),                
                }
class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    
    def tare_change(self, cr, uid, ids,weight_net_manual,weight_manual):
        res =  weight_manual - weight_net_manual    
        return {'value': {
                'tare': res,
                }}
        
    def weight_manual_change(self, cr, uid, ids,tare,weight_net_manual):
        res =  weight_net_manual + tare
        return {'value': {
                'weight_manual': res,
                }}
    
    _columns = {
                'seals_first' : fields.integer('Seal first'),
                'seals_last' : fields.integer('Seal last'), 
                'volume' : fields.float('volume'),    
                'tare' : fields.float('tare'),   
                'weight_manual' : fields.float('weight'), 
                'weight_net_manual' : fields.float('weight net'),
                }
