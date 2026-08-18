from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AdvancedPaymentRegisterWizard(models.TransientModel):
    _name = "advanced.payment.register.wizard"
    _description = "Advanced Payment Register"

    payment_date = fields.Date(
        string="Payment Date",
        default=fields.Date.context_today,
        required=True,
    )
    amount = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Payment Journal",
        domain="[('type', 'in', ['bank', 'cash', 'credit']), ('company_id', '=', company_id)]",
        required=True,
        check_company=True,
    )
    payment_method_line_id = fields.Many2one(
        comodel_name="account.payment.method.line",
        string="Payment Method",
        compute="_compute_payment_method_line_id",
        domain="[('id', 'in', available_payment_method_line_ids)]",
        readonly=False,
        store=True,
        required=True,
    )
    available_payment_method_line_ids = fields.Many2many(
        comodel_name="account.payment.method.line",
        compute="_compute_available_payment_method_line_ids",
    )
    payment_type = fields.Selection(
        selection=[
            ("outbound", "Send Money"),
            ("inbound", "Receive Money"),
        ],
        default="outbound",
        required=True,
    )
    contract_id = fields.Many2one(
        comodel_name="contract.project",
        string="Contract",
    )
    contract_invoice_id = fields.Many2one(
        comodel_name="contract.invoice",
        string="Contract Invoice",
    )
    memo = fields.Char(
        string="Memo",
        required=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Vendor",
        required=True,
    )

    @api.depends("payment_type", "journal_id")
    def _compute_available_payment_method_line_ids(self):
        for wizard in self:
            wizard.available_payment_method_line_ids = (
                wizard.journal_id._get_available_payment_method_lines(wizard.payment_type)
                if wizard.journal_id
                else False
            )

    @api.depends("available_payment_method_line_ids")
    def _compute_payment_method_line_id(self):
        for wizard in self:
            available_lines = wizard.available_payment_method_line_ids
            if wizard.payment_method_line_id not in available_lines:
                wizard.payment_method_line_id = available_lines[:1]

    @api.onchange("journal_id")
    def _onchange_journal_id(self):
        for wizard in self:
            if wizard.journal_id:
                wizard.company_id = wizard.journal_id.company_id
                wizard.currency_id = (
                    wizard.journal_id.currency_id
                    or wizard.journal_id.company_id.currency_id
                )

    @api.constrains("amount")
    def _check_amount(self):
        for wizard in self:
            if wizard.amount <= 0:
                raise ValidationError(_("The payment amount must be greater than zero."))

    def action_register_payment(self):
        self.ensure_one()
        if not self.payment_method_line_id:
            raise ValidationError(_("Please select a payment method."))

        currency = self.journal_id.currency_id or self.journal_id.company_id.currency_id
        payment = self.env["account.payment"].create({
            "partner_id": self.partner_id.id,
            "contract_id": self.contract_id.id or False,
            "contract_invoice_id": self.contract_invoice_id.id or False,
            "journal_id": self.journal_id.id,
            "company_id": self.journal_id.company_id.id,
            "currency_id": currency.id,
            "partner_type": "supplier",
            "payment_type": self.payment_type,
            "payment_method_line_id": self.payment_method_line_id.id,
            "amount": self.amount,
            "date": self.payment_date,
            "memo": self.memo,
        })
        payment.action_post()
        return {"type": "ir.actions.act_window_close"}
