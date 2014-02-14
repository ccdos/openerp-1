from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp


class stock_move(osv.osv):
    _inherit = 'stock.move'
    
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        product_obj = self.pool.get('product.template')
        product_obj = product_obj.browse(cr, uid, product_id, context=context)
        location_dest_id = product_obj.property_stock_production.id
        
        return {
                'value':{
                         'location_dest_id':location_dest_id,
                         }
                }
    
    def weight_manual_change(self, cr, uid, ids,tare,weight_net):
        res =  weight_net + tare
        volume = float(weight_net/100.00)  
        return {'value': {
                'weight': res,
                'volume': volume,
                }}
        
    def _cal_move_weight(self, cr, uid, ids, name, args, context=None):
        res = {}
        uom_obj = self.pool.get('product.uom')
        for move in self.browse(cr, uid, ids, context=context):
            weight = weight_net = 0.00
            if move.product_id.weight > 0.00:
                converted_qty = move.product_qty

                if move.product_uom.id <> move.product_id.uom_id.id:
                    converted_qty = uom_obj._compute_qty(cr, uid, move.product_uom.id, move.product_qty, move.product_id.uom_id.id)

                weight = (converted_qty * move.product_id.weight)

                if move.product_id.weight_net > 0.00:
                    weight_net = (converted_qty * move.product_id.weight_net)

            res[move.id] =  {
                            'weight': weight + move.tare,
                            'weight_net': weight_net,
                            }
        return res

    _columns = {
        'tare' : fields.float('tare', digits_compute= dp.get_precision('Stock Weight')),     
        'seals_first' : fields.integer('Seal first'),
        'seals_last' : fields.integer('Seal last'),     
        'weight': fields.function(_cal_move_weight, type='float', string='Weight', digits_compute= dp.get_precision('Stock Weight'), multi='_cal_move_weight',
                  store={
                 'stock.move': (lambda self, cr, uid, ids, c=None: ids, ['product_id', 'product_qty', 'product_uom'], 20),
                 }),
        'weight_net': fields.function(_cal_move_weight, type='float', string='Net weight', digits_compute= dp.get_precision('Stock Weight'), multi='_cal_move_weight',
                  store={
                 'stock.move': (lambda self, cr, uid, ids, c=None: ids, ['product_id', 'product_qty', 'product_uom'], 20),
                 }),
        'weight_uom_id': fields.many2one('product.uom', 'Unit of Measure', required=True,readonly="1",help="Unit of Measure (Unit of Measure) is the unit of measurement for Weight",),
        }
    
 
    
stock_move()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def _cal_weight(self, cr, uid, ids, name, args, context=None):
        res = {}
        uom_obj = self.pool.get('product.uom')
        for picking in self.browse(cr, uid, ids, context=context):
            total_weight = total_weight_net = total_tare = packages = volume = 0.00

            for move in picking.move_lines:
                total_weight += move.weight
                total_weight_net += move.weight_net
                total_tare += move.tare 
                packages += 1
            
            volume += float(total_weight_net/100)
            res[picking.id] = {
                                'weight': total_weight,
                                'weight_net': total_weight_net,
                                'tare': total_tare,
                                'number_of_packages': packages,
                                'volume':volume,
                              }
        return res


    def _get_picking_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            result[line.picking_id.id] = True
        return result.keys()

    _columns = {
        'tare' : fields.function(_cal_weight, type='float', string='Tare', digits_compute= dp.get_precision('Stock Weight'), multi='_cal_weight',
                  store={
                 'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                 'stock.move': (_get_picking_line, ['product_id','product_qty','product_uom','product_uos_qty'], 20),
                 }),   
        'volume': fields.function(_cal_weight, type='float', string='Volume', digits_compute= dp.get_precision('Stock Weight'), multi='_cal_weight',
                  store={
                 'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                 'stock.move': (_get_picking_line, ['product_id','product_qty','product_uom','product_uos_qty'], 20),
                 }),   
        'weight': fields.function(_cal_weight, type='float', string='Weight', digits_compute= dp.get_precision('Stock Weight'), multi='_cal_weight',
                  store={
                 'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                 'stock.move': (_get_picking_line, ['product_id','product_qty','product_uom','product_uos_qty'], 20),
                 }),
        'weight_net': fields.function(_cal_weight, type='float', string='Net Weight', digits_compute= dp.get_precision('Stock Weight'), multi='_cal_weight',
                  store={
                 'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                 'stock.move': (_get_picking_line, ['product_id','product_qty','product_uom','product_uos_qty'], 20),
                 }),
        'number_of_packages': fields.function(_cal_weight, type='integer', string='Number_of_packages',  multi='_cal_weight',
                  store={
                 'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                 'stock.move': (_get_picking_line, ['product_id','product_qty','product_uom','product_uos_qty'], 20),
                 }),  
        'weight_uom_id': fields.many2one('product.uom', 'Unit of Measure', required=True,readonly="1",help="Unit of measurement for Weight",),
        'carrier_id':fields.many2one("delivery.carrier","Carrier"),
        'carrier_tracking_ref': fields.text('Carrier Tracking Ref'),
        
        }

stock_picking()

class stock_picking_out(osv.osv):
    _inherit = 'stock.picking.out'
    def weight_manual_change(self, cr, uid, ids,tare,weight_net):
        res =  weight_net + tare
        volume = float(weight_net/100.00)  
        return {'value': {
                'weight': res,
                'volume': volume,
                }}
    def _cal_weight(self, cr, uid, ids, name, args, context=None):
        return self.pool.get('stock.picking')._cal_weight(cr, uid, ids, name, args, context=context)


    def _get_picking_line(self, cr, uid, ids, context=None):
        return self.pool.get('stock.picking')._get_picking_line(cr, uid, ids, context=context)

    _columns = {
        'volume': fields.function(_cal_weight, type='float', string='Volume', digits_compute= dp.get_precision('Stock Weight'), multi='_cal_weight',
                  store={
                 'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                 'stock.move': (_get_picking_line, ['product_id','product_qty','product_uom','product_uos_qty'], 20),
                 }),   
        'tare' : fields.function(_cal_weight, type='float', string='Tare', digits_compute= dp.get_precision('Stock Weight'), multi='_cal_weight',
                  store={
                 'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                 'stock.move': (_get_picking_line, ['product_id','product_qty','product_uom','product_uos_qty'], 20),
                 }),  
        'carrier_id':fields.many2one("delivery.carrier","Carrier"),
        'weight': fields.function(_cal_weight, type='float', string='Weight', digits_compute= dp.get_precision('Stock Weight'), multi='_cal_weight',
                  store={
                 'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                 'stock.move': (_get_picking_line, ['product_id','product_qty','product_uom','product_uos_qty'], 20),
                 }),
        'weight_net': fields.function(_cal_weight, type='float', string='Net Weight', digits_compute= dp.get_precision('Stock Weight'), multi='_cal_weight',
                  store={
                 'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                 'stock.move': (_get_picking_line, ['product_id','product_qty','product_uom','product_uos_qty'], 20),
                 }),
        'carrier_tracking_ref': fields.text('Carrier Tracking Ref'),
        'number_of_packages': fields.function(_cal_weight, type='integer', string='Number_of_packages',  multi='_cal_weight',
                  store={
                 'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                 'stock.move': (_get_picking_line, ['product_id','product_qty','product_uom','product_uos_qty'], 20),
                 }),  
        }
stock_picking_out()

class stock_picking_in(osv.osv):
    _inherit = 'stock.picking.in'

    def _cal_weight(self, cr, uid, ids, name, args, context=None):
        return self.pool.get('stock.picking')._cal_weight(cr, uid, ids, name, args, context=context)

    def _get_picking_line(self, cr, uid, ids, context=None):
        return self.pool.get('stock.picking')._get_picking_line(cr, uid, ids, context=context)
    
    _columns = {
        'volume': fields.function(_cal_weight, type='float', string='Volume', digits_compute= dp.get_precision('Stock Weight'), multi='_cal_weight',
                  store={
                 'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                 'stock.move': (_get_picking_line, ['product_id','product_qty','product_uom','product_uos_qty'], 20),
                 }),    
        'tare' : fields.function(_cal_weight, type='float', string='Tare', digits_compute= dp.get_precision('Stock Weight'), multi='_cal_weight',
                  store={
                 'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                 'stock.move': (_get_picking_line, ['product_id','product_qty','product_uom','product_uos_qty'], 20),
                 }),  
        #'number_of_packages': fields.integer('Number of Packages'),
        'weight': fields.function(_cal_weight, type='float', string='Weight', digits_compute= dp.get_precision('Stock Weight'), multi='_cal_weight',
                store={
                'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                'stock.move': (_get_picking_line, ['product_id','product_qty','product_uom','product_uos_qty'], 20),
                }),
        'weight_net': fields.function(_cal_weight, type='float', string='Net Weight', digits_compute= dp.get_precision('Stock Weight'), multi='_cal_weight',
                store={
                'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                'stock.move': (_get_picking_line, ['product_id','product_qty','product_uom','product_uos_qty'], 20),
                }),
        'carrier_tracking_ref': fields.text('Carrier Tracking Ref'),
        'number_of_packages': fields.function(_cal_weight, type='integer', string='Number_of_packages',  multi='_cal_weight',
                  store={
                 'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                 'stock.move': (_get_picking_line, ['product_id','product_qty','product_uom','product_uos_qty'], 20),
                 }),  
        }
 
stock_picking_in()
