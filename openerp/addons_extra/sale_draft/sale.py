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

class sale_order_line(orm.Model):
    _inherit = "sale.order.line"  
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
        