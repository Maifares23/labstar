from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    contract_id = fields.Many2one(
        comodel_name="contract.project",
        string="Contract",
        copy=False,
        index=True,
    )
    contract_invoice_id = fields.Many2one(
        comodel_name="contract.invoice",
        string="Contract Invoice",
        copy=False,
        index=True,
    )
