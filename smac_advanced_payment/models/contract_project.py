from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ContractProject(models.Model):
    _inherit = "contract.project"

    amount_due = fields.Float(
        string="Amount Due",
        compute="_compute_amount_due",
    )
    payment_count = fields.Integer(
        string="Payment Count",
        compute="_compute_payment_count",
    )

    @api.depends("advanced_payment_amount")
    def _compute_amount_due(self):
        Payment = self.env["account.payment"]
        for contract in self:
            paid_amount = sum(
                Payment.search([
                    ("contract_id", "=", contract.id),
                    ("state", "in", ["in_process", "paid"]),
                ]).mapped("amount")
            )
            contract.amount_due = (contract.advanced_payment_amount or 0.0) - paid_amount

    def _compute_payment_count(self):
        Payment = self.env["account.payment"]
        for contract in self:
            contract.payment_count = Payment.search_count([
                ("contract_id", "=", contract.id),
            ])

    def payment_view_button(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Payments"),
            "res_model": "account.payment",
            "target": "current",
            "view_mode": "list,form",
            "domain": [("contract_id", "=", self.id)],
            "context": {"create": False},
        }

    def action_register_sales_payment(self):
        self.ensure_one()
        if not self.subcontractor_id:
            raise ValidationError(_("Please set a subcontractor before registering a payment."))

        journal = self.env["account.journal"].search([
            ("type", "in", ["bank", "cash", "credit"]),
            ("company_id", "=", self.env.company.id),
        ], limit=1)
        if not journal:
            raise ValidationError(_("Please configure a bank, cash, or credit journal first."))

        view = self.env.ref(
            "smac_advanced_payment.advanced_payment_register_wizard_view_form"
        )
        return {
            "name": _("Register Payment"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "advanced.payment.register.wizard",
            "views": [(view.id, "form")],
            "target": "new",
            "context": {
                "default_amount": max(self.amount_due, 0.0),
                "default_memo": _("Advanced Payment For %s") % self.display_name,
                "default_contract_id": self.id,
                "default_journal_id": journal.id,
                "default_partner_id": self.subcontractor_id.id,
                "default_payment_type": "outbound",
                "default_company_id": journal.company_id.id,
                "default_currency_id": (
                    journal.currency_id or journal.company_id.currency_id
                ).id,
            },
        }
