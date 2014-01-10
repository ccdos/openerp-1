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
from openerp.tools.translate import _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare

class sale_order(orm.Model):
    _inherit = "sale.order"
    _columns = {
            'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)],'progress': [('readonly', False)], 'sent': [('readonly', False)]}, help="Pricelist for current sales order."),
    }
    def action_cancel_draft(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        cr.execute('select id from sale_order_line where order_id IN %s and state=%s', (tuple(ids), 'cancel'))
        line_ids = map(lambda x: x[0], cr.fetchall())
        self.write(cr, uid, ids, {'state': 'draft', 'invoice_ids': [], 'shipped': 0})
        self.pool.get('sale.order.line').write(cr, uid, line_ids, {'invoiced': False, 'state': 'draft', 'invoice_lines': [(6, 0, [])]})
        wf_service = netsvc.LocalService("workflow")
        for inv_id in ids:
            wf_service.trg_delete(uid, 'sale.order', inv_id, cr)
            wf_service.trg_create(uid, 'sale.order', inv_id, cr)
        return True
    
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
        for proc_id in proc_ids:
            wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)

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

class sale_order_line(orm.Model):
    _inherit = "sale.order.line"  
    _columns = {
            'date_delay': fields.date('Date Delay', required=True, readonly=False),
            }
    def change_date_delay(self, cr, uid, ids,date_delay, date_order, context=None):
        date_delay_format = datetime.strptime(date_delay, DEFAULT_SERVER_DATE_FORMAT)
        date_order_format = datetime.strptime(date_order, DEFAULT_SERVER_DATE_FORMAT)
        date = ( date_delay_format - date_order_format).days
        if date < 0:
            msgalert = {'title':'Warning','message':'The delay date have to be greater than the order date.'}
            return {'value': {
            'delay': 0,
            'date_delay':date_order,
            },'warning':msgalert}
            
        return {'value': {
            'delay': date,
            }}
        
    def change_delay(self, cr, uid, ids, date_order, delay, context=None):
        date_order_format = datetime.strptime(date_order, DEFAULT_SERVER_DATE_FORMAT)
        date_planned = date_order_format + relativedelta(days=delay or 0.0)
        date = date_planned.strftime(DEFAULT_SERVER_DATE_FORMAT)
        return {'value': {
            'date_delay': date,
            }}
        
    def action_recalculate(self, cr, uid, ids, *args):
        result = {}
        sale_obj = self.pool.get('sale.order')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        for r in self.browse(cr, uid, ids):
            sale_id = r.order_id.id
            sale = sale_obj.browse(cr, uid, sale_id)
            pricelist = sale.pricelist_id.id
            date_order = sale.date_order
            product = r.product_id.id
            qty = r.product_uom_qty
            partner_id = r.order_partner_id.id
            uom = r.product_uom.id
            if partner_id:
                lang = partner_obj.browse(cr, uid, partner_id).lang
            context_partner = {'lang': lang, 'partner_id': partner_id}
            product_obj = product_obj.browse(cr, uid, product, context=context_partner)
            #price_get(self, cr, uid, ids, prod_id, qty, partner=None, context=None)
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom,
                        'date': date_order,
                        })[pricelist]
                        
            if price is False:
                warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist.")

                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                self.write(cr, uid, [r.id], {'price_unit': price})
        