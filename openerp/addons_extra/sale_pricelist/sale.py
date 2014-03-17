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
import openerp.addons.decimal_precision as dp
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from openerp.tools import  DEFAULT_SERVER_DATETIME_FORMAT



class sale_order_line(orm.Model):
    _inherit = "sale.order.line"  
    _columns = {
            'date_delay': fields.date('Date Delay', required=True, readonly=False),
            }
 
    def category_parent(self,cr, uid,categ_id):
        category_mov_obj = self.pool.get('product.category')
        for line in category_mov_obj.browse(cr, uid, [categ_id]):
            parent_id = line.parent_id.id
            if parent_id:
                return parent_id
            else:
                return False
            
    def category_parent_recursive(self,cr, uid,categ_id,list=[]): 
        value = self.category_parent(cr, uid, categ_id)
        if value and value not in list:
            return [value] + self.category_parent_recursive(cr, uid, value, list+[value])
        else:
            return []
         
    def change_price_unit(self, cr, uid, ids,price_unit, product, order_id, pricelist_id,date_order, context=None):
        if product == False:
            return False
        if pricelist_id == False:
            return False
        if date_order == False:
            return False
        product_obj = self.pool.get('product.product').browse(cr, uid, product)
        product_obj_template = product_obj.product_tmpl_id
        categ_id = product_obj_template.categ_id.id
        categ_ids = [categ_id] + self.category_parent_recursive(cr, uid,categ_id)
        date_order = datetime.strptime(date_order, '%Y-%m-%d')
        
        price_list_version = 0
        price_list_item_mov_obj = self.pool.get('product.pricelist.item')
        ids_price_list_item = price_list_item_mov_obj.search(cr,uid,[],0, None)
        price_list_item = []
        for line in price_list_item_mov_obj.browse(cr, uid, ids_price_list_item):
            try:
                line_pricelist_id = line.price_version_id.pricelist_id.id 
                line_product_id = line.product_id.id
                line_categ_id = line.categ_id.id
                if line_categ_id == False:
                    line_categ_id = 1
                if line_pricelist_id == pricelist_id:
                    if (line_product_id and line_product_id == product) or line_categ_id in categ_ids:
                        line_version_date_start = line.price_version_id.date_start
                        if line_version_date_start:
                            line_version_date_start = datetime.strptime(line_version_date_start, '%Y-%m-%d')
                        line_version_date_end = line.price_version_id.date_end
                        if line_version_date_end:
                            line_version_date_end = datetime.strptime(line_version_date_end, '%Y-%m-%d')
                        if (line_version_date_start and (date_order < line_version_date_start)) or (line_version_date_end and (date_order > line_version_date_end)):
                            pass
                        else:
                            price_list_item.append(line)
            except:
                print "error: line.price_version_id.pricelist_id"
            
        if len(price_list_item)==0:
            price_list_version_mov_obj = self.pool.get('product.pricelist.version')
            ids_price_list_version = price_list_version_mov_obj.search(cr,uid,[],0, None)
            for line in price_list_version_mov_obj.browse(cr, uid, ids_price_list_version):
                if line.pricelist_id.id == pricelist_id:
                    line_version_date_start = line.date_start
                    if line_version_date_start:
                        line_version_date_start = datetime.strptime(line_version_date_start, '%Y-%m-%d')
                    line_version_date_end = line.date_end
                    if line_version_date_end:
                        line_version_date_end = datetime.strptime(line_version_date_end, '%Y-%m-%d')
                    if (line_version_date_start and (date_order < line_version_date_start)) or (line_version_date_end and (date_order > line_version_date_end)):
                            pass
                    else:
                        
                        price_list_version = line.id
                        price_surcharge = price_unit - product_obj_template.list_price
                        price_list_item_mov_obj.create(cr, uid, {
                                    'base':1,
                                    'price_version_id':price_list_version,
                                    'price':price_unit,
                                    'product_id': product,
                                    'categ_id': '',
                                    'price_min_margin':0.000,
                                    'price_max_margin':0.000,
                                    'price_round': 0.000,
                                    'price_surcharge':price_surcharge,
                                     },context)
                        return False
                
        return True
    
    
class product_pricelist_item(osv.osv):
    _inherit = "product.pricelist.item"
    _columns = {
        'price': fields.float('Price',
            digits_compute= dp.get_precision('Product Price'), help='Specify the price.'),    
    }
    
    def change_price(self, cr, uid, ids, price, product, categ_id, base, context=None):
        if product == False:
            return False
        if base == 1:
            product_obj = self.pool.get('product.product').browse(cr, uid, product)
            product_obj_template = product_obj.product_tmpl_id
            price_surcharge = price - product_obj_template.list_price
            return {
                    'value':{
                             'price_surcharge': price_surcharge
                             }
                    }
        elif base == 2:
            product_obj = self.pool.get('product.product').browse(cr, uid, product)
            product_obj_template = product_obj.product_tmpl_id
            price_surcharge = price - product_obj_template.standard_price
            return {
                    'value':{
                             'price_surcharge': price_surcharge
                             }
                    }
        else:
            return {
                    'value':{
                             'price_surcharge': 0.00,
                             'price': '',
                             }
                    }
            
    
product_pricelist_item()

class product_pricelist_version(osv.osv):
    _inherit = "product.pricelist.version"
    def _default_name(self, cr, uid, context=None):
        today = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return 'version ' + today
    
    def _default_date_start(self, cr, uid, context=None):
        today = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return today

    _defaults = {
        'name': _default_name,
        'date_start': _default_date_start
    }
    
    
    
    