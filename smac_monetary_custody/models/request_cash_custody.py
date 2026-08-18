from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError


class RequestCashCustody(models.Model):
    _name = "request.cash.custody"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]
    _description = "Request Cash Custody"
    _order = "id desc"

    name = fields.Char(
        string="Reference",
        default=lambda self: _("New"),
        readonly=True,
        copy=False,
        index=True,
        tracking=True,
    )
    requester_id = fields.Many2one(
        comodel_name="res.users",
        string="Requester",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )
    project_id = fields.Many2one(
        comodel_name="construction.project",
        string="Project",
        required=True,
        tracking=True,
    )
    date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    request_custody_lines_ids = fields.One2many(
        comodel_name="request.cash.custody.lines",
        inverse_name="request_custody_id",
        string="Lines",
        copy=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("sent_to_confirmation", "Sent To Confirmation"),
            ("submit", "Submit"),
            ("confirm", "Confirm"),
            ("paid", "Paid"),
        ],
        string="State",
        default="draft",
        required=True,
        copy=False,
        tracking=True,
    )
    total_amount = fields.Float(
        string="Total Amount",
        compute="_compute_total_amount",
        store=True,
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Journal",
    )
    debit_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Debit Account",
    )
    credit_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Credit Account",
    )
    journal_entry_count = fields.Integer(
        string="Entries Count",
        compute="_compute_journal_entry_count",
    )

    def _compute_journal_entry_count(self):
        Move = self.env["account.move"]
        for request in self:
            request.journal_entry_count = Move.search_count([
                ("request_custody_id", "=", request.id),
                ("move_type", "=", "entry"),
            ])

    def view_journal_entry_button(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Journal Entries"),
            "res_model": "account.move",
            "target": "current",
            "view_mode": "list,form",
            "domain": [
                ("request_custody_id", "=", self.id),
                ("move_type", "=", "entry"),
            ],
            "context": {"create": False},
        }

    @api.depends("request_custody_lines_ids.amount")
    def _compute_total_amount(self):
        for request in self:
            request.total_amount = sum(request.request_custody_lines_ids.mapped("amount"))

    def action_sent_to_confirmation(self):
        self.write({"state": "sent_to_confirmation"})

    def action_submit(self):
        self.write({"state": "submit"})

    def action_confirm(self):
        for request in self:
            if not request.request_custody_lines_ids:
                raise ValidationError(_("Please add at least one custody line."))
        self.write({"state": "confirm"})

    def action_paid(self):
        for request in self:
            if request.state != "confirm":
                raise ValidationError(_("Only confirmed custody requests can be paid."))
            if request.total_amount <= 0:
                raise ValidationError(_("The total custody amount must be greater than zero."))
            if not request.journal_id or not request.debit_account_id or not request.credit_account_id:
                raise ValidationError(_("Please set the journal, debit account, and credit account."))
            if request.debit_account_id == request.credit_account_id:
                raise ValidationError(_("Debit and credit accounts must be different."))

            company = request.journal_id.company_id
            currency = company.currency_id
            move = self.env["account.move"].create({
                "move_type": "entry",
                "date": request.date,
                "ref": request.display_name,
                "company_id": company.id,
                "currency_id": currency.id,
                "journal_id": request.journal_id.id,
                "request_custody_id": request.id,
                "line_ids": [
                    Command.create({
                        "name": request.display_name,
                        "debit": request.total_amount,
                        "credit": 0.0,
                        "account_id": request.debit_account_id.id,
                        "currency_id": currency.id,
                    }),
                    Command.create({
                        "name": request.display_name,
                        "debit": 0.0,
                        "credit": request.total_amount,
                        "account_id": request.credit_account_id.id,
                        "currency_id": currency.id,
                    }),
                ],
            })
            move.action_post()
            request.state = "paid"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals.get("name") == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "request.cash.custody.Sequence"
                ) or _("New")
        return super().create(vals_list)


class RequestCashCustodyLines(models.Model):
    _name = "request.cash.custody.lines"
    _description = "Request Cash Custody Line"
    _order = "id"

    request_custody_id = fields.Many2one(
        comodel_name="request.cash.custody",
        string="Request Custody",
        required=True,
        ondelete="cascade",
        index=True,
    )
    account_id = fields.Many2one(
        comodel_name="account.account",
        string="Account",
        domain="[('account_type', 'in', ['expense', 'expense_depreciation', 'expense_direct_cost'])]",
        required=True,
    )
    amount = fields.Float(
        string="Amount",
        required=True,
    )

    @api.constrains("amount")
    def _check_positive_amount(self):
        for line in self:
            if line.amount <= 0:
                raise ValidationError(_("Amount must be greater than zero."))
