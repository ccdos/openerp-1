from openerp.osv import fields, osv

class base_extend(osv.osv):
  
  _inherit = "res.company"
  _columns = {
    'registry_mercantil': fields.text('registry mercantil'),
    'lpd': fields.text('data protection law'),
    'footer1': fields.text('footer 1'),
    'footer2': fields.text('footer 2'),
    'footer3': fields.text('footer 3'),
    'rml_header4': fields.text('RML Header Shipping'),
  }
   
base_extend()