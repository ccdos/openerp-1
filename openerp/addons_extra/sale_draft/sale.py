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
                return False
            else:
                self.write(cr, uid, [r.id], {'price_unit': price})
                return True
        