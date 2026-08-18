from odoo import models, fields

class ResArea(models.Model):
    _name = 'res.area'
    _description = 'Area'

    name = fields.Char(required=True)
    state_id = fields.Many2one('res.country.state', string='State', required=True)
