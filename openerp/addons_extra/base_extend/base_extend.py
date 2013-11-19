from openerp.osv import fields, osv

class base_extend(osv.osv):
  
  _inherit = "res.company"
  _columns = {
    'registry_mercantil': fields.text('registry mercantil'),
    'lpd': fields.text('data protection law'),
  }
   
base_extend()