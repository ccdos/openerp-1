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

from openerp.report import report_sxw

class rmlparser(report_sxw.rml_parse):
    def set_context(self, objects, data, ids, report_type = None):
        super(rmlparser,self).set_context(objects, data, ids, report_type)
        self.setCompany(objects[0])

report_sxw.report_sxw('report.preview.report.apaisado', 'res.company',
      'addons/base_extend/report/preview_report_apaisado.rml', parser=rmlparser, header='internal landscape')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
