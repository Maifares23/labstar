from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    contract_down_payment_id = fields.Many2one('contract.down.payment', string="Down Payment", readonly=True)
