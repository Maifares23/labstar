from odoo import api, fields, models


class FlexableInstallment(models.Model):
    _name = 'flexable.installment'
    _description = 'Flexable Installment'

    date = fields.Date(
        string='Date',
        required=False)
    amount = fields.Float(
        string='Amount',
        required=False)
    rental_id = fields.Many2one(
        comodel_name='rental.contract',
        string='Rental',
        required=False)