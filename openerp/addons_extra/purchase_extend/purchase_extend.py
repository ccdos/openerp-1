from openerp.osv import fields, osv

class purchase_extend(osv.osv):
  
  _inherit = "purchase.order"
  _columns = {
    #'registry_mercantil': fields.text('registry mercantil'),
  }
   
base_extend()