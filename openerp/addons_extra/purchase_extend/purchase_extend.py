from openerp.osv import fields, osv

class purchase_extend(osv.osv):
  
  _inherit = "purchase.order"
  _columns = {
    'informe': fields.text('registry mercantil'),
    'lpd': fields.text('data protection law'),
  }
   
base_extend()