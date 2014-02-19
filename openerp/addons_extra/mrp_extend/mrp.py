# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 jmesteve All Rights Reserved
#                       https://github.com/jmesteve
#                       <jmesteve@me.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv, orm
from openerp import netsvc
from openerp.tools.translate import _
from openerp.tools import float_compare
from datetime import datetime
from dateutil.relativedelta import relativedelta

class mrp_production(osv.osv):
    _inherit = "mrp.production"
    
    def _src_id_default(self, cr, uid, ids, context=None):
        try:
            location_id = 7
            product_obj = self.pool.get('stock.location')
            product_obj = product_obj.browse(cr, uid, location_id, context=context)
            name = product_obj.name
            return location_id
        except:
            try:
                location_model, location_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'stock_location_stock')
                self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
            except (orm.except_orm, ValueError):
                location_id = False
            return location_id
    
    def _dest_id_default(self, cr, uid, ids, context=None):
        try:
            location_id = 11
            product_obj = self.pool.get('stock.location')
            product_obj = product_obj.browse(cr, uid, location_id, context=context)
            name = product_obj.name
            return location_id
        except:
            try:
                location_model, location_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'stock_location_stock')
                self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
            except (orm.except_orm, ValueError):
                location_id = False
            return location_id
    
    def button_action_revert_done(self, cr, uid, ids, context=None):
    
        if not len(ids):
            return False
        for reg in self.browse(cr, uid, ids, context):
            if reg.state in ("cancel","confirmed","in_production","picking_except","done"):
                self.write(cr, uid, [reg.id], {'state': 'draft'})
                return True
        return False
    def button_action_done(self, cr, uid, ids, context=None):
    
        if not len(ids):
            return False
        for reg in self.browse(cr, uid, ids, context):
            if reg.state in ("in_production"):
                self.write(cr, uid, [reg.id], {'state': 'done'})
                return True
        return False
    def button_action_ready(self, cr, uid, ids, context=None):
    
        if not len(ids):
            return False
        for reg in self.browse(cr, uid, ids, context):
            if reg.state in ("draft"):
                self.write(cr, uid, [reg.id], {'state': 'ready'})
                return True
        return False
    
    def action_produce(self, cr, uid, production_id, production_qty, production_mode, context=None):
        """ To produce final product based on production mode (consume/consume&produce).
        If Production mode is consume, all stock move lines of raw materials will be done/consumed.
        If Production mode is consume & produce, all stock move lines of raw materials will be done/consumed
        and stock move lines of final product will be also done/produced.
        @param production_id: the ID of mrp.production object
        @param production_qty: specify qty to produce
        @param production_mode: specify production mode (consume/consume&produce).
        @return: True
        """
        stock_mov_obj = self.pool.get('stock.move')
        production = self.browse(cr, uid, production_id, context=context)

        wf_service = netsvc.LocalService("workflow")
        if not production.move_lines and production.state == 'ready':
            # trigger workflow if not products to consume (eg: services)
            wf_service.trg_validate(uid, 'mrp.production', production_id, 'button_produce', cr)

        produced_qty = 0
        for produced_product in production.move_created_ids2:
            if (produced_product.scrapped) or (produced_product.product_id.id != production.product_id.id):
                continue
            produced_qty += produced_product.product_qty
        
        if production_mode in ['consume','consume_produce','consume_done']:
            consumed_data = {}

            # Calculate already consumed qtys
            for consumed in production.move_lines2:
                if consumed.scrapped:
                    continue
                if not consumed_data.get(consumed.product_id.id, False):
                    consumed_data[consumed.product_id.id] = 0
                consumed_data[consumed.product_id.id] += consumed.product_qty

            # Find product qty to be consumed and consume it
            for scheduled in production.product_lines:

                # total qty of consumed product we need after this consumption
                total_consume = ((production_qty + produced_qty) * scheduled.product_qty / production.product_qty)

                # qty available for consume and produce
                qty_avail = scheduled.product_qty - consumed_data.get(scheduled.product_id.id, 0.0)

                if float_compare(qty_avail, 0, precision_rounding=scheduled.product_id.uom_id.rounding) <= 0:
                    # there will be nothing to consume for this raw material
                    continue

                raw_product = [move for move in production.move_lines if move.product_id.id==scheduled.product_id.id]
                if raw_product:
                    # qtys we have to consume
                    qty = total_consume - consumed_data.get(scheduled.product_id.id, 0.0)
                    if float_compare(qty, qty_avail, precision_rounding=scheduled.product_id.uom_id.rounding) == 1:
                        # if qtys we have to consume is more than qtys available to consume
                        prod_name = scheduled.product_id.name_get()[0][1]
                        raise osv.except_osv(_('Warning!'), _('You are going to consume total %s quantities of "%s".\nBut you can only consume up to total %s quantities.') % (qty, prod_name, qty_avail))
                    if float_compare(qty, 0, precision_rounding=scheduled.product_id.uom_id.rounding) <= 0:                        
                        # we already have more qtys consumed than we need
                        continue

                    raw_product[0].action_consume(qty, raw_product[0].location_id.id, context=context)

        if production_mode == 'consume_produce':
            # To produce remaining qty of final product
            #vals = {'state':'confirmed'}
            #final_product_todo = [x.id for x in production.move_created_ids]
            #stock_mov_obj.write(cr, uid, final_product_todo, vals)
            #stock_mov_obj.action_confirm(cr, uid, final_product_todo, context)
            produced_products = {}
            for produced_product in production.move_created_ids2:
                if produced_product.scrapped:
                    continue
                if not produced_products.get(produced_product.product_id.id, False):
                    produced_products[produced_product.product_id.id] = 0
                produced_products[produced_product.product_id.id] += produced_product.product_qty

            for produce_product in production.move_created_ids:
                produced_qty = produced_products.get(produce_product.product_id.id, 0)
                subproduct_factor = self._get_subproduct_factor(cr, uid, production.id, produce_product.id, context=context)
                rest_qty = (subproduct_factor * production.product_qty) - produced_qty

                if rest_qty < (subproduct_factor * production_qty):
                    prod_name = produce_product.product_id.name_get()[0][1]
                    raise osv.except_osv(_('Warning!'), _('You are going to produce total %s quantities of "%s".\nBut you can only produce up to total %s quantities.') % ((subproduct_factor * production_qty), prod_name, rest_qty))
                if rest_qty > 0 :
                    stock_mov_obj.action_consume(cr, uid, [produce_product.id], (subproduct_factor * production_qty), context=context)
        elif production_mode == 'consume_done':
            self.write(cr, uid, [production_id], {'state': 'done'})
            ids = stock_mov_obj.search(cr,uid,[],0, None)
            for line in stock_mov_obj.browse(cr, uid, ids):
                if line.name == production.name and line.product_id == production.product_id:
                   stock_mov_obj.write(cr, uid, [line.id], {'state': 'draft'})
                   stock_mov_obj.unlink(cr, uid,[line.id])
                

        for raw_product in production.move_lines2:
            new_parent_ids = []
            parent_move_ids = [x.id for x in raw_product.move_history_ids]
            for final_product in production.move_created_ids2:
                if final_product.id not in parent_move_ids:
                    new_parent_ids.append(final_product.id)
            for new_parent_id in new_parent_ids:
                stock_mov_obj.write(cr, uid, [raw_product.id], {'move_history_ids': [(4,new_parent_id)]})

        wf_service.trg_validate(uid, 'mrp.production', production_id, 'button_produce_done', cr)
        return True
    
    _defaults = {
        'location_src_id': _src_id_default,
        'location_dest_id': _dest_id_default
    }

mrp_production()

class mrp_product_produce(osv.osv_memory):
    _inherit = "mrp.product.produce"
    _columns = {
        'mode': fields.selection([('consume_produce', 'Consume & Produce'),
                                  ('consume', 'Consume Only'),
                                  ('consume_done', 'Consume & Done')
                                  ], 'Mode', required=True,
                                  help="'Consume only' mode will only consume the products with the quantity selected.\n"
                                        "'Consume & Produce' mode will consume as well as produce the products with the quantity selected "
                                        "and it will finish the production order when total ordered quantities are produced."),
    }
    _defaults = {
         'mode': lambda *x: 'consume_done'
    }
    
class procurement_order(osv.osv):
    _inherit = 'procurement.order'    
    def _src_id_default(self, cr, uid, ids, context=None):
        try:
            location_id = 7
            product_obj = self.pool.get('stock.location')
            product_obj = product_obj.browse(cr, uid, location_id, context=context)
            name = product_obj.name
            return location_id
        except:
            try:
                location_model, location_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'stock_location_stock')
                self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
            except (orm.except_orm, ValueError):
                location_id = False
            return location_id
    
    def _dest_id_default(self, cr, uid, ids, context=None):
        try:
            location_id = 11
            product_obj = self.pool.get('stock.location')
            product_obj = product_obj.browse(cr, uid, location_id, context=context)
            name = product_obj.name
            return location_id
        except:
            try:
                location_model, location_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'stock_location_stock')
                self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
            except (orm.except_orm, ValueError):
                location_id = False
            return location_id
    
    
    def make_mo(self, cr, uid, ids, context=None):
        """ Make Manufacturing(production) order from procurement
        @return: New created Production Orders procurement wise 
        """
        res = {}
        company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
        production_obj = self.pool.get('mrp.production')
        move_obj = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        procurement_obj = self.pool.get('procurement.order')
        for procurement in procurement_obj.browse(cr, uid, ids, context=context):
            res_id = procurement.move_id.id
            newdate = datetime.strptime(procurement.date_planned, '%Y-%m-%d %H:%M:%S') - relativedelta(days=procurement.product_id.produce_delay or 0.0)
            newdate = newdate - relativedelta(days=company.manufacturing_lead)
            produce_id = production_obj.create(cr, uid, {
                'origin': procurement.origin,
                'product_id': procurement.product_id.id,
                'product_qty': procurement.product_qty,
                'product_uom': procurement.product_uom.id,
                'product_uos_qty': procurement.product_uos and procurement.product_uos_qty or False,
                'product_uos': procurement.product_uos and procurement.product_uos.id or False,
                'location_src_id': procurement_obj._src_id_default(cr, uid, ids, context),
                'location_dest_id': procurement_obj._dest_id_default(cr, uid, ids, context),
                'bom_id': procurement.bom_id and procurement.bom_id.id or False,
                'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                'move_prod_id': res_id,
                'company_id': procurement.company_id.id,
            })
            
            res[procurement.id] = produce_id
            self.write(cr, uid, [procurement.id], {'state': 'running', 'production_id': produce_id})   
            bom_result = production_obj.action_compute(cr, uid,
                    [produce_id], properties=[x.id for x in procurement.property_ids])
            #wf_service.trg_validate(uid, 'mrp.production', produce_id, 'button_confirm', cr)
        self.production_order_create_note(cr, uid, ids, context=context)
        return res
