from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ContractInvoice(models.Model):
    _inherit = "contract.invoice"

    payment_count = fields.Integer(
        string="Payment Count",
        compute="_compute_payment_count",
    )

    def _compute_payment_count(self):
        Payment = self.env["account.payment"]
        for invoice in self:
            invoice.payment_count = Payment.search_count([
                ("contract_invoice_id", "=", invoice.id),
            ])

    def payment_view_button(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Payments"),
            "res_model": "account.payment",
            "target": "current",
            "view_mode": "list,form",
            "domain": [("contract_invoice_id", "=", self.id)],
            "context": {"create": False},
        }

    def action_register_sales_payment(self):
        self.ensure_one()
        partner = self.contract_project_id.subcontractor_id
        if not partner:
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
                "default_amount": self.outstanding_payment_for_this_period or 0.0,
                "default_memo": _("Advanced Payment For %s") % self.display_name,
                "default_contract_invoice_id": self.id,
                "default_journal_id": journal.id,
                "default_partner_id": partner.id,
                "default_payment_type": "outbound",
                "default_company_id": journal.company_id.id,
                "default_currency_id": (
                    journal.currency_id or journal.company_id.currency_id
                ).id,
            },
        }
