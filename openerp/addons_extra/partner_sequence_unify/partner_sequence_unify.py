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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class res_partner(orm.Model):
    _inherit = 'res.partner'
    _columns = {
        'ref': fields.char('Reference', size=64, select=True, required=True),                          
        }
    _sql_constraints = [
        ('uniq_reference', 'unique(ref)', "The reference must be unique"),
        ]
    _defaults = {
        'ref': '/',
        }
# new register
    def create(self, cr, uid, vals, context=None):  
        if not 'ref' in vals or vals['ref'] == '/':
                vals['ref'] = self.pool.get('ir.sequence').get(cr, uid, 'res.partner')                  
        return super(res_partner, self).create(cr, uid, vals, context)

# edit register
    def write(self, cr, uid, ids, vals, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        partners_without_code = self.search(cr, uid, [
            ('ref', 'in', [False, '/']), ('id', 'in', ids)], context=context)
        direct_write_ids = set(ids) - set(partners_without_code)
        super(res_partner, self).write(
            cr, uid, list(direct_write_ids), vals, context)
        for partner_id in partners_without_code:
                vals['ref'] = self.pool.get('ir.sequence').get(cr, uid, 'res.partner')    
                super(res_partner, self).write(cr, uid, partner_id, vals, context)
        return True

    def copy(self, cr, uid, id, default={}, context=None):
        product = self.read(cr, uid, id, ['ref'], context=context)
        if product['ref']:
            default.update({
                'ref': product['ref'] + _('-copy'),
            })

        return super(res_partner, self).copy(cr, uid, id, default, context)
