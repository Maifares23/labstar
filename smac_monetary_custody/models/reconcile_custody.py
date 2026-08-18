from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError


class ReconcileCustody(models.Model):
    _name = "reconcile.cash.custody"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]
    _description = "Reconcile Cash Custody"
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
    date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    reconcile_custody_lines_ids = fields.One2many(
        comodel_name="reconcile.cash.custody.lines",
        inverse_name="reconcile_custody_id",
        string="Lines",
        copy=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("sent_to_confirmation", "Sent To Confirmation"),
            ("submit", "Submit"),
            ("confirm", "Confirm"),
            ("reconciled", "Reconciled"),
        ],
        string="State",
        default="draft",
        required=True,
        copy=False,
        tracking=True,
    )
    total_reconciled_amount = fields.Float(
        string="Total Reconciled Amount",
        compute="_compute_total_reconciled_amount",
        store=True,
    )
    journal_entry_count = fields.Integer(
        string="Entries Count",
        compute="_compute_journal_entry_count",
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Journal",
    )
    credit_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Credit Account",
    )

    def _compute_journal_entry_count(self):
        Move = self.env["account.move"]
        for reconciliation in self:
            reconciliation.journal_entry_count = Move.search_count([
                ("reconcile_custody_id", "=", reconciliation.id),
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
                ("reconcile_custody_id", "=", self.id),
                ("move_type", "=", "entry"),
            ],
            "context": {"create": False},
        }

    @api.onchange("requester_id")
    def _onchange_requester_id(self):
        for reconciliation in self:
            commands = [Command.clear()]
            if reconciliation.requester_id:
                requests = self.env["request.cash.custody"].search([
                    ("requester_id", "=", reconciliation.requester_id.id),
                    ("state", "in", ["confirm", "paid"]),
                ])
                for request in requests:
                    for line in request.request_custody_lines_ids:
                        already_reconciled = sum(
                            self.env["reconcile.cash.custody.lines"].search([
                                ("reconcile_custody_id.state", "in", ["confirm", "reconciled"]),
                                ("request_custody_line_id", "=", line.id),
                            ]).mapped("reconciled_amount")
                        )
                        remaining = line.amount - already_reconciled
                        if remaining > 0:
                            commands.append(Command.create({
                                "account_id": line.account_id.id,
                                "amount": remaining,
                                "project_id": line.request_custody_id.project_id.id,
                                "request_custody_line_id": line.id,
                                "reconciled_amount": 0.0,
                            }))
            reconciliation.reconcile_custody_lines_ids = commands

    @api.depends("reconcile_custody_lines_ids.reconciled_amount")
    def _compute_total_reconciled_amount(self):
        for reconciliation in self:
            reconciliation.total_reconciled_amount = sum(
                reconciliation.reconcile_custody_lines_ids.mapped("reconciled_amount")
            )

    def action_sent_to_confirmation(self):
        self.write({"state": "sent_to_confirmation"})

    def action_submit(self):
        self.write({"state": "submit"})

    def action_confirm(self):
        for reconciliation in self:
            if not reconciliation.reconcile_custody_lines_ids:
                raise ValidationError(_("No custody lines are available to reconcile."))
            if reconciliation.total_reconciled_amount <= 0:
                raise ValidationError(_("Enter a reconciled amount greater than zero."))
        self.write({"state": "confirm"})

    def action_reconciled(self):
        for reconciliation in self:
            if reconciliation.state != "confirm":
                raise ValidationError(_("Only confirmed custody reconciliations can be posted."))
            if reconciliation.total_reconciled_amount <= 0:
                raise ValidationError(_("The total reconciled amount must be greater than zero."))
            if not reconciliation.journal_id or not reconciliation.credit_account_id:
                raise ValidationError(_("Please set the journal and credit account."))

            company = reconciliation.journal_id.company_id
            currency = company.currency_id
            move_lines = []
            for line in reconciliation.reconcile_custody_lines_ids:
                if line.reconciled_amount <= 0:
                    continue
                line_vals = {
                    "name": reconciliation.display_name,
                    "debit": line.reconciled_amount,
                    "credit": 0.0,
                    "account_id": line.account_id.id,
                    "currency_id": currency.id,
                }
                analytic_account = line.project_id.analytic_account_id
                if analytic_account:
                    line_vals["analytic_distribution"] = {
                        str(analytic_account.id): 100.0,
                    }
                move_lines.append(Command.create(line_vals))

            move_lines.append(Command.create({
                "name": reconciliation.display_name,
                "debit": 0.0,
                "credit": reconciliation.total_reconciled_amount,
                "account_id": reconciliation.credit_account_id.id,
                "currency_id": currency.id,
            }))

            move = self.env["account.move"].create({
                "move_type": "entry",
                "date": reconciliation.date,
                "ref": reconciliation.display_name,
                "company_id": company.id,
                "currency_id": currency.id,
                "journal_id": reconciliation.journal_id.id,
                "reconcile_custody_id": reconciliation.id,
                "line_ids": move_lines,
            })
            move.action_post()
            reconciliation.state = "reconciled"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals.get("name") == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "reconcile.cash.custody.Sequence"
                ) or _("New")
        return super().create(vals_list)


class ReconcileCashCustodyLines(models.Model):
    _name = "reconcile.cash.custody.lines"
    _description = "Reconcile Cash Custody Line"
    _order = "id"

    reconcile_custody_id = fields.Many2one(
        comodel_name="reconcile.cash.custody",
        string="Reconcile Custody",
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
        string="Available Amount",
        required=True,
        readonly=True,
    )
    project_id = fields.Many2one(
        comodel_name="construction.project",
        string="Project",
        required=True,
    )
    reconciled_amount = fields.Float(
        string="Reconciled Amount",
        required=True,
        default=0.0,
    )
    request_custody_line_id = fields.Many2one(
        comodel_name="request.cash.custody.lines",
        string="Request Cash Custody Line",
        required=True,
        ondelete="restrict",
        index=True,
    )

    @api.constrains("reconciled_amount", "amount")
    def _check_reconciled_amount(self):
        for line in self:
            if line.reconciled_amount < 0:
                raise ValidationError(_("The reconciled amount cannot be negative."))
            if line.reconciled_amount > line.amount:
                raise ValidationError(_("The reconciled amount cannot exceed the available amount."))
