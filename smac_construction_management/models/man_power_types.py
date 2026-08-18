from odoo import api, fields, models


class ManPowerTypes(models.Model):
    _name = 'man.power.types'
    _description = 'Man Power Types'

    name = fields.Char(required=True)
    project_id = fields.Many2one(
        comodel_name='construction.project',
        string='Project',
        required=True)
