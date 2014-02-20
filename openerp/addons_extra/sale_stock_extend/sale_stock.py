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

from openerp.osv import fields, orm
from openerp import netsvc

class sale_order(orm.Model):
    _inherit = "sale.order"
    _columns = {
            'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)],'progress': [('readonly', False)], 'sent': [('readonly', False)]}, help="Pricelist for current sales order."),
            'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('procurement', 'Procurement'),
            ('procurement_purchase', 'Procurement Purchase'),
            ('procurement_production', 'Procurement Production'),
            ('procurement_all', 'Procurement All'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange',
            help="Gives the status of the quotation or sales order. \nThe exception status is automatically set when a cancel operation occurs in the processing of a document linked to the sales order. \nThe 'Waiting Schedule' status is set when the invoice is confirmed but waiting for the scheduler to run on the order date.", select=True),
        
    }
    def action_wait(self, cr, uid, ids, context=None):
        context = context or {}
        for o in self.browse(cr, uid, ids):
            if not o.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a sales order which has no line.'))
            noprod = self.test_no_product(cr, uid, o, context)
            if (o.order_policy == 'manual') or noprod:
                self.write(cr, uid, [o.id], {'state': 'manual', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
            else:
                self.write(cr, uid, [o.id], {'state': 'procurement', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
            self.pool.get('sale.order.line').button_confirm(cr, uid, [x.id for x in o.order_line])
        return True
    
    def action_progress(self, cr, uid, ids, context=None):
        context = context or {}
        for o in self.browse(cr, uid, ids):
           if not o.order_line:
               raise osv.except_osv(_('Error!'),_('You cannot confirm a sales order which has no line.'))
           noprod = self.test_no_product(cr, uid, o, context)
           if (o.order_policy == 'manual') or noprod:
               self.write(cr, uid, [o.id], {'state': 'manual', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
           else:
               self.write(cr, uid, [o.id], {'state': 'progress', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
           self.pool.get('sale.order.line').button_confirm(cr, uid, [x.id for x in o.order_line])
        return True
    
    def action_procurement(self, cr, uid, ids, context= None, *args):
        if not len(ids):
            return False
        
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'procurement', 'procurement_form_view')
        view_id = view_ref and view_ref[1] or False,
#        
        procurement_mov_obj = self.pool.get('procurement.order')
        sale = self.browse(cr, uid, ids[0], context=context)
        sale_name = sale.name
        ids_procurement = procurement_mov_obj.search(cr,uid,[],0, None)
        ids_selected =[]
        for line in procurement_mov_obj.browse(cr, uid, ids_procurement):
            origin = line.origin
            if origin == sale_name:
               ids_selected.append(line.id)
        
        ids_selected_len = len(ids_selected)
        if ids_selected_len == 1:
            return {
                 'type': 'ir.actions.act_window',
                 'name': 'Procurement',
                 'view_mode': 'form',
                 'view_type': 'form',
                 'view_id': view_id,
                 'res_model': 'procurement.order',
                 'nodestroy': True,
                 'res_id': ids_selected[0], # assuming the many2one
                 'target':'new',  # 'current for the current window' 'new for the new window'
                 'context': context,
            }
            
        elif ids_selected_len > 1:
            return {
                 'type': 'ir.actions.act_window',
                 'name': 'Procurement',
                 'view_mode': 'tree,form',
                 'view_type': 'form',
                 'res_model': 'procurement.order',
                 'target':'new',
                 'context': context,
                 'domain': [('id', 'in', ids_selected)],
           }
        else:
            return False
    def action_mrp(self, cr, uid, ids, context= None, *args):
        if not len(ids):
            return False
        
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mrp', 'mrp_production_form_view')
        view_id = view_ref and view_ref[1] or False,
#        
        mrp_mov_obj = self.pool.get('mrp.production')
        sale = self.browse(cr, uid, ids[0], context=context)
        sale_name = sale.name
        ids_mrp = mrp_mov_obj.search(cr,uid,[],0, None)
        ids_selected =[]
        for line in mrp_mov_obj.browse(cr, uid, ids_mrp):
            origin = line.origin
            if origin == sale_name:
               ids_selected.append(line.id)
        
        ids_selected_len = len(ids_selected)
        if ids_selected_len == 1:
            return {
                 'type': 'ir.actions.act_window',
                 'name': 'Mrp',
                 'view_mode': 'form',
                 'view_type': 'form',
                 'view_id': view_id,
                 'res_model': 'mrp.production',
                 'nodestroy': True,
                 'res_id': ids_selected[0], # assuming the many2one
                 'target':'new',  # 'current for the current window' 'new for the new window'
                 'context': context,
            }
            
        elif ids_selected_len > 1:
            return {
                 'type': 'ir.actions.act_window',
                 'name': 'Mrp',
                 'view_mode': 'tree,form',
                 'view_type': 'form',
                 'res_model': 'mrp.production',
                 'target':'new',
                 'context': context,
                 'domain': [('id', 'in', ids_selected)],
           }
        else:
            return False
        
    def action_purchase(self, cr, uid, ids, context= None, *args):
        if not len(ids):
            return False
        
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'purchase', 'purchase_order_form')
        view_id = view_ref and view_ref[1] or False,
#        
        purchase_mov_obj = self.pool.get('purchase.order')
        sale = self.browse(cr, uid, ids[0], context=context)
        sale_name = sale.name
        ids_purchase = purchase_mov_obj.search(cr,uid,[],0, None)
        ids_selected =[]
        for line in purchase_mov_obj.browse(cr, uid, ids_purchase):
            origin = line.origin
            if origin == sale_name:
               ids_selected.append(line.id)
        
        ids_selected_len = len(ids_selected)
        if ids_selected_len == 1:
            return {
                 'type': 'ir.actions.act_window',
                 'name': 'Purchase',
                 'view_mode': 'form',
                 'view_type': 'form',
                 'view_id': view_id,
                 'res_model': 'purchase.order',
                 'nodestroy': True,
                 'res_id': ids_selected[0], # assuming the many2one
                 'target':'new',  # 'current for the current window' 'new for the new window'
                 'context': context,
            }
            
        elif ids_selected_len > 1:
            return {
                 'type': 'ir.actions.act_window',
                 'name': 'Purchase',
                 'view_mode': 'tree,form',
                 'view_type': 'form',
                 'res_model': 'purchase.order',
                 'target':'new',
                 'context': context,
                 'domain': [('id', 'in', ids_selected)],
           }
        else:
            return False
    
    def _prepare_order_line_procurement(self, cr, uid, order, line, move_id, date_planned, date_order, context=None):
        return {
            'name': line.name,
            'origin': order.name,
            'date_order': date_order,
            'date_planned': date_planned,
            'product_id': line.product_id.id,
            'product_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': (line.product_uos and line.product_uos_qty)\
                    or line.product_uom_qty,
            'product_uos': (line.product_uos and line.product_uos.id)\
                    or line.product_uom.id,
            'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
            'procure_method': line.type,
            'move_id': move_id,
            'company_id': order.company_id.id,
            'note': line.name,
            'property_ids': [(6, 0, [x.id for x in line.property_ids])],
        }
    
    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, date_order, context=None):
        location_id = order.shop_id.warehouse_id.lot_stock_id.id
        output_id = order.shop_id.warehouse_id.lot_output_id.id
        return {
            'name': line.name,
            'picking_id': picking_id,
            'product_id': line.product_id.id,
            'date': date_order,
            'date_expected': date_planned,
            'product_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
            'product_uos': (line.product_uos and line.product_uos.id)\
                    or line.product_uom.id,
            'product_packaging': line.product_packaging.id,
            'partner_id': line.address_allotment_id.id or order.partner_shipping_id.id,
            'location_id': location_id,
            'location_dest_id': output_id,
            'sale_line_id': line.id,
            'tracking_id': False,
            'state': 'draft',
            #'state': 'waiting',
            'company_id': order.company_id.id,
            'price_unit': line.product_id.standard_price or 0.0
        }
            
    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        """Create the required procurements to supply sales order lines, also connecting
        the procurements to appropriate stock moves in order to bring the goods to the
        sales order's requested location.

        If ``picking_id`` is provided, the stock moves will be added to it, otherwise
        a standard outgoing picking will be created to wrap the stock moves, as returned
        by :meth:`~._prepare_order_picking`.

        Modules that wish to customize the procurements or partition the stock moves over
        multiple stock pickings may override this method and call ``super()`` with
        different subsets of ``order_lines`` and/or preset ``picking_id`` values.

        :param browse_record order: sales order to which the order lines belong
        :param list(browse_record) order_lines: sales order line records to procure
        :param int picking_id: optional ID of a stock picking to which the created stock moves
                               will be added. A new picking will be created if ommitted.
        :return: True
        """
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        procurement_obj = self.pool.get('procurement.order')
        proc_ids = []

        for line in order_lines:
            if line.state == 'done':
                continue

            date_planned = self._get_date_planned(cr, uid, order, line, order.date_order, context=context)

            if line.product_id:
                if line.product_id.type in ('product', 'consu'):
                    if not picking_id:
                        picking_id = picking_obj.create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
                    move_id = move_obj.create(cr, uid, self._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned,order.date_order, context=context))
                else:
                    # a service has no stock move
                    move_id = False

                proc_id = procurement_obj.create(cr, uid, self._prepare_order_line_procurement(cr, uid, order, line, move_id, date_planned, order.date_order, context=context))
                proc_ids.append(proc_id)
                line.write({'procurement_id': proc_id})
                self.ship_recreate(cr, uid, order, line, move_id, proc_id)

        wf_service = netsvc.LocalService("workflow")
        if picking_id:
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        #for proc_id in proc_ids:
        #    wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)

        val = {}
        if order.state == 'shipping_except':
            val['state'] = 'progress'
            val['shipped'] = False

            if (order.order_policy == 'manual'):
                for line in order.order_line:
                    if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                        val['state'] = 'manual'
                        break
        order.write(val)
        return True