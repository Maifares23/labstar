from odoo import api, fields, models


class Equipments(models.Model):
    _name = 'equipments'
    _description = 'Equipments'

    name = fields.Char(required=True)
    project_id = fields.Many2one(
        comodel_name='construction.project',
        string='Project',
        required=True)
