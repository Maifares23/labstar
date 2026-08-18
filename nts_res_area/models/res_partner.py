from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    area_id = fields.Many2one('res.area', string='Area', domain="[('state_id','=',state_id)]")
    additional_notes = fields.Text('Additional Notes')  # Add this field to store additional notes
    full_address = fields.Text('Full Address')