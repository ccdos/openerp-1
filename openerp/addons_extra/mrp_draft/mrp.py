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

class mrp_production(orm.Model):
    _inherit = "mrp.production"
    
    def action_revert_done(self, cr, uid, ids, context=None):
    
        if not len(ids):
            return False
        for reg in self.browse(cr, uid, ids, context):
            if reg.state in ("cancel","confirmed","in_production","picking_except","done"):
                self.write(cr, uid, [reg.id], {'state': 'draft'})
                return True
        return False
    def action_done(self, cr, uid, ids, context=None):
    
        if not len(ids):
            return False
        for reg in self.browse(cr, uid, ids, context):
            if reg.state in ("in_production"):
                self.write(cr, uid, [reg.id], {'state': 'done'})
                return True
        return False
    def action_ready(self, cr, uid, ids, context=None):
    
        if not len(ids):
            return False
        for reg in self.browse(cr, uid, ids, context):
            if reg.state in ("draft"):
                self.write(cr, uid, [reg.id], {'state': 'ready'})
                return True
        return False

