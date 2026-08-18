from odoo import api, fields, models


class IncreaseRatioLines(models.Model):
    _name = 'increase.ratio.line'
    _description = 'Increase Ratio Lines'

    date = fields.Date(
        string='Date',
        required=False)
    amount = fields.Float(
        string='Amount',
        required=False)
    fixed_amount = fields.Float(
        string='Amount',
        required=False, )
    ratio = fields.Float(
        string='Ratio%',
        required=False)
    fixed_ratio = fields.Float(
        string='Ratio%',
        required=False, compute="_compute_fixed_amount")
    amount_total = fields.Float(
        string='Total Amount',
        required=False, compute="_compute_total_amount")
    rental_id = fields.Many2one(
        comodel_name='rental.contract',
        string='Rental',
        required=False)

    @api.depends("rental_id.rental_fee", "ratio", "rental_id.increased_rent_type", "fixed_amount")
    def _compute_total_amount(self):
        for line in self:
            rental_id = line.rental_id
            amount = rental_id.rental_fee
            line.amount_total = amount * line.ratio * 0.01 if rental_id.increased_rent_type == 'ratio' else line.fixed_amount if rental_id.increased_rent_type == 'fixed_ratio' else 0

    @api.depends("rental_id.rental_fee", "fixed_amount")
    def _compute_fixed_amount(self):
        for line in self:
            line.fixed_ratio = 0
            rental_id = line.rental_id
            amount = rental_id.rental_fee
            line.fixed_ratio = (line.fixed_amount / amount) * 100 if amount > 0 else 0
