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
 
from openerp.osv import orm, fields, osv
from openerp.tools.translate import _
 
class inherit_res_partner(osv.osv):
    _inherit = 'res.partner'
    _name = 'res.partner'
    _columns = {
        'property_account_payable': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Account Payable",
            view_load=True,
            domain="[('type', '=', 'payable')]",
            help="This account will be used instead of the default one as the payable account for the current partner",
            required=False),
        'property_account_receivable': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Account Receivable",
            view_load=True,
            domain="[('type', '=', 'receivable')]",
            help="This account will be used instead of the default one as the receivable account for the current partner",
            required=False),          
        } 
    
def create(self, cr, uid, vals, context=None):  
        #if not 'ref' in vals or vals['ref'] == '/':
        #        vals['ref'] = self.pool.get('ir.sequence').get(cr, uid, 'res.partner')                  
        #return super(res_partner, self).create(cr, uid, vals, context)
        vals[property_account_payable] = '430000001'
        return super(res_partner, self).create(cr, uid, vals, context)
    
inherit_res_partner()


       
     
