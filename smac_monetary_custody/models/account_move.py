from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    request_custody_id = fields.Many2one(
        comodel_name="request.cash.custody",
        string="Request Cash Custody",
        copy=False,
        index=True,
        ondelete="set null",
    )
    reconcile_custody_id = fields.Many2one(
        comodel_name="reconcile.cash.custody",
        string="Reconcile Cash Custody",
        copy=False,
        index=True,
        ondelete="set null",
    )
