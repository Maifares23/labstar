# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PdcPayment(models.Model):
    _name = "pdc.payment"
    _description = "PDC Payment"
    _rec_name = "cheque_ref"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    invoice_ids = fields.Many2many('account.move', 'account_invoice_pdc_rel', 'pdc_id', 'invoice_id', string="Invoices",
                                   readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, )
    state = fields.Selection(
        [('draft', 'Draft'), ('register', 'Registered'), ('return', 'Returned'), ('deposit', 'Deposited'),
         ('bounce', 'Bounced'), ('done', 'Collected'), ('cancel', 'Cancelled')], readonly=True, default='draft',
        string="Status")

    deposit_journal_id = fields.Many2one('account.journal', string='Bank Journal',
                                         domain=[('type', 'in', ['bank']), ('pdc_type', '=', False)])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, )
    due_date = fields.Date(string='Due Date', default=fields.Date.context_today, required=True)
    collection_date = fields.Date(string="Collection Date")

    deposit_date = fields.Date(string='Deposit Date')
    bounce_date = fields.Date(string='Bounce Date')
    return_date = fields.Date(string='Return Date')
    physically_received = fields.Boolean(string="Physically Received", default=False)
    enable_deposit_entry = fields.Boolean(string="Enable Deposit Entry", compute="_compute_enable_deposit_entry")

    communication = fields.Char(string='Memo')
    cheque_ref = fields.Char('Cheque Reference', copy=False)
    agent = fields.Char('Agent')
    bank = fields.Many2one('res.bank', string="Bank")
    name = fields.Char(related="returned_entry.name", string="Name", readonly=True, store=True)
    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money')], string='Payment Type',
                                    required=True, )
    batch_id = fields.Many2one('batch.pdc.payment', string='Batch', invisible=True)
    registered_deposit_entry = fields.Many2one('account.move', string="Registered Deposit Entry", copy=False)
    returned_entry = fields.Many2one('account.move', string="Returned Entry", copy=False)

    available_journal_ids = fields.Many2many('account.journal', compute='_compute_available_journal_ids')
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain="[('id', 'in', available_journal_ids)]")
    print_original_cash_back_receipt = fields.Boolean(string="Print Original Cash/Back Receipt", default=True,
                                                      copy=False)
    print_vendor_receipt = fields.Boolean(string="Print Vendor Receipt", default=True, copy=False)
    customer_pdc = fields.Integer(string="Customer PDC", default=0)
    vendor_pdc = fields.Integer(string="Vendor PDC", default=0)
    @api.onchange("payment_type")
    def onchange_payment_type(self):
        if self.journal_id:
            self.journal_id = False

    @api.constrains("cheque_ref", "partner_id")
    def _check_cheque_ref_partner(self):
        for pdc_payment in self.filtered(lambda p: p.cheque_ref):
            if self.search_count([("id", "!=", pdc_payment.id), ("partner_id", "=", pdc_payment.partner_id.id),
                                  ("cheque_ref", "=", pdc_payment.cheque_ref)]) != 0:
                raise ValidationError(_("You can't duplicate cheque reference %s for customer %s" % (
                    pdc_payment.cheque_ref, pdc_payment.partner_id.display_name)))

    @api.constrains("cheque_ref")
    def _check_cheque_ref(self):
        for pdc_payment in self.filtered(lambda p: p.cheque_ref):
            if not pdc_payment.cheque_ref.isdigit():
                raise ValidationError(
                    _("The Cheque Reference %s must be a sequence of digits." % pdc_payment.cheque_ref))

    @api.depends("payment_type")
    def _compute_available_journal_ids(self):
        account_journal_obj = self.env["account.journal"]
        for pdc_payment in self:
            domain = []
            if pdc_payment.payment_type == "inbound":
                domain = [("pdc_type", "=", "pdc_received")]
            elif pdc_payment.payment_type == "outbound":
                domain = [("pdc_type", "=", "pdc_issued")]
            pdc_payment.available_journal_ids = account_journal_obj.search(domain)

    @api.depends("state")
    def _compute_enable_deposit_entry(self):
        for pdc_payment in self:
            pdc_payment.enable_deposit_entry = pdc_payment.company_id.enable_deposit_entry if pdc_payment.vendor_pdc > 0 else True

    @api.onchange("communication")
    def _onchange_communication(self):
        self.invoice_ids.ref = self.communication

    @api.onchange("journal_id")
    def onchange_journal(self):
        currency_id = False
        if self.journal_id:
            journal = self.journal_id
            currency_id = journal.currency_id or journal.company_id.currency_id or self.env.user.company_id.currency_id
            currency_id = currency_id.id

        self.currency_id = currency_id

    def write(self, vals):
        if 'cheque_ref' in vals:
            for pdc in self:
                entries = self.env['account.move'].search([('pdc_ref_id', '=', pdc.id)])
                for line in entries.line_ids:
                    line.name = f"Check NO. {vals.get('cheque_ref', '')}"
        return super(PdcPayment, self).write(vals)

    @api.model
    def default_get(self, default_fields):
        rec = super(PdcPayment, self).default_get(default_fields)

        # Determine payment type based on context and update rec
        if self._context.get('default_customer_pdc', False):
            rec['payment_type'] = 'inbound'  # Default to inbound for Customer PDC
        elif self._context.get('default_vendor_pdc', False):
            rec['payment_type'] = 'outbound'  # Default to outbound for Vendor PDC

        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')

        # Check for selected invoices ids
        if not active_ids or active_model != 'account.move':
            return rec

        invoices = self.env['account.move'].browse(active_ids).filtered(
            lambda move: move.is_invoice(include_receipts=True))
        lines = invoices.line_ids

        # Check all invoices are open
        if not invoices or any(invoice.state != 'posted' for invoice in invoices):
            raise UserError(_("You can only register payments for open invoices"))

        # Check if, in batch payments, there are not negative invoices and positive invoices
        dtype = invoices[0].move_type
        for inv in invoices[1:]:
            if inv.move_type != dtype:
                if ((dtype == 'in_refund' and inv.move_type == 'in_invoice') or
                        (dtype == 'in_invoice' and inv.move_type == 'in_refund')):
                    raise UserError(_(
                        "You cannot register Post dated cheques for vendor bills and supplier refunds at the same time."))
                if ((dtype == 'out_refund' and inv.move_type == 'out_invoice') or
                        (dtype == 'out_invoice' and inv.move_type == 'out_refund')):
                    raise UserError(_(
                        "You cannot register Post dated cheques for customer invoices and credit notes at the same time."))

        amount = sum(lines.mapped('amount_residual'))
        rec.update({
            'currency_id': invoices[0].currency_id.id,
            'amount': abs(amount),
            'partner_id': invoices[0].commercial_partner_id.id,
            'communication': invoices[0].payment_reference or invoices[0].ref or invoices[0].name,
            'invoice_ids': [(6, 0, invoices.ids)],
        })
        # Finalize payment type based on amount if not already set
        if 'payment_type' not in rec:
            rec['payment_type'] = 'inbound' if amount > 0 else 'outbound'

        return rec

    @api.ondelete(at_uninstall=False)
    def _unlink_if_draft(self):
        for pdc_payment in self:
            if pdc_payment.state != "draft":
                raise ValidationError(_(f"You can't delete {pdc_payment.name} ,because it is not in draft state."))

    def action_cancel(self):
        self.filtered(lambda p: p.state == "draft").write({"state": "cancel"})

    def _prepare_move_line(self, date, account_id, currency, amount_currency, debit=0, credit=0):
        return {
            "name": _("Check NO. %s" % self.cheque_ref),
            "amount_currency": amount_currency,
            "currency_id": self.company_id.currency_id != self.currency_id and self.currency_id.id or currency.id,
            "debit": debit,
            "credit": credit,
            "date_maturity": date,
            "partner_id": self.partner_id.id,
            "account_id": account_id
        }

    def _prepare_journal_entry(self, date, move_lines, currency):
        return {
            "date": date,
            "ref": self.communication,
            "journal_id": self.journal_id.id,
            "currency_id": currency.id,
            "partner_id": self.partner_id.id,
            "pdc_ref_id": self.id,
            "line_ids": move_lines
        }

    def action_register(self):
        account_move_obj = self.env["account.move"]

        # Process each PDC payment in draft state
        for pdc_payment in self.filtered(lambda p: p.state == "draft"):
            if not pdc_payment.journal_id.default_account_id:
                raise UserError(_("Configuration Error: Please define an account for the PDC payment."))

            invoices = pdc_payment.invoice_ids
            company_currency = invoices and invoices.company_id.currency_id or pdc_payment.company_id.currency_id

            # Convert the amount if the payment currency differs from the company's currency
            if pdc_payment.currency_id != company_currency:
                balance = pdc_payment.currency_id._convert(
                    pdc_payment.amount,
                    company_currency,
                    pdc_payment.company_id,
                    pdc_payment.due_date
                )
            else:
                balance = pdc_payment.amount

            # Determine account logic based on context flags
            if self._context.get('default_customer_pdc', False):
                account_id = pdc_payment.partner_id.property_account_receivable_id.id
                if pdc_payment.payment_type == "inbound":
                    pdc_credit_account_id = account_id
                    pdc_debit_account_id = pdc_payment.journal_id.default_account_id.id
                else:
                    pdc_credit_account_id = pdc_payment.journal_id.default_account_id.id
                    pdc_debit_account_id = account_id

            elif self._context.get('default_vendor_pdc', False):
                account_id = pdc_payment.partner_id.property_account_payable_id.id
                if pdc_payment.payment_type == "inbound":
                    pdc_credit_account_id = account_id
                    pdc_debit_account_id = pdc_payment.journal_id.default_account_id.id
                else:
                    pdc_credit_account_id = pdc_payment.journal_id.default_account_id.id
                    pdc_debit_account_id = account_id

            else:
                # Default logic based on payment type
                if pdc_payment.payment_type == "inbound":
                    account_id = pdc_payment.partner_id.property_account_receivable_id.id
                    pdc_credit_account_id = account_id
                    pdc_debit_account_id = pdc_payment.journal_id.default_account_id.id
                else:
                    account_id = pdc_payment.partner_id.property_account_payable_id.id
                    pdc_credit_account_id = pdc_payment.journal_id.default_account_id.id
                    pdc_debit_account_id = account_id

            # Calculate amount currency
            amount_currency = pdc_payment.amount if company_currency != pdc_payment.currency_id else balance

            currency = pdc_payment.journal_id.currency_id or pdc_payment.currency_id

            # Prepare move lines
            move_lines = [
                (0, 0, pdc_payment._prepare_move_line(
                    pdc_payment.due_date,
                    pdc_debit_account_id,
                    currency,
                    amount_currency,
                    debit=balance
                )),
                (0, 0, pdc_payment._prepare_move_line(
                    pdc_payment.due_date,
                    pdc_credit_account_id,
                    currency,
                    -amount_currency,
                    credit=balance
                ))
            ]

            # Create and post journal entry
            move = account_move_obj.create(
                pdc_payment._prepare_journal_entry(pdc_payment.payment_date, move_lines, currency)
            )
            move.action_post()

            # Reconcile the lines with invoice lines
            domain = [
                ('account_type', 'in', ('asset_receivable', 'liability_payable')),
                ('reconciled', '=', False)
            ]
            lines = move.line_ids
            inv_lines = invoices.line_ids.filtered_domain(domain)

            for account in inv_lines.account_id:
                (inv_lines + lines).filtered_domain(
                    [("account_id", "=", account.id), ("reconciled", "=", False)]
                ).reconcile()

            # Update payment state and link returned journal entry
            pdc_payment.write({"state": "register", "returned_entry": move.id})

    def action_return_cheque(self):
        account_move_reversal_obj = self.env["account.move.reversal"]
        account_move_obj = self.env["account.move"]

        for pdc_payment in self.filtered(lambda p: p.state in ["deposit", "register", "bounce"]):
            if not pdc_payment.return_date:
                raise UserError(_("Return Date is required."))

            if pdc_payment.returned_entry:
                reversed_entry_wizard = account_move_reversal_obj.with_context(
                    active_model="account.move", active_ids=pdc_payment.returned_entry.ids).create({
                    "reason": "Registered Entry",
                    "journal_id": pdc_payment.journal_id.id,
                    "date": pdc_payment.return_date
                })

                res = reversed_entry_wizard.reverse_moves()
                reversed_entry = account_move_obj.browse(res["res_id"])
                reversed_entry.write({"pdc_ref_id": pdc_payment.id})

            pdc_payment.write({"state": "return"})

    def action_deposit(self):
        account_move_obj = self.env["account.move"]

        for pdc_payment in self.filtered(lambda p: p.state in ["register", "bounce"]):
            customer_pdc_payment_account_id = pdc_payment.company_id.customer_pdc_payment_account_id
            vendor_pdc_payment_account_id = pdc_payment.company_id.vendor_pdc_payment_account_id
            if not pdc_payment.enable_deposit_entry:
                pdc_payment.write({"state": "deposit"})
            else:
                if not pdc_payment.deposit_date:
                    raise UserError(_("Deposit Date is required."))

                if not pdc_payment.deposit_journal_id:
                    raise UserError(_("You should fill in the Bank Journal."))

                if not customer_pdc_payment_account_id or not vendor_pdc_payment_account_id:
                    raise UserError(_("Configuration Error: Please define accounts for the PDC payment."))

                invoices = pdc_payment.invoice_ids
                account_id = pdc_payment.journal_id.default_account_id.id

                company_currency_id = invoices and invoices.company_id.currency_id or pdc_payment.company_id.currency_id

                if pdc_payment.currency_id != pdc_payment.company_id.currency_id:
                    balance = pdc_payment.currency_id._convert(pdc_payment.amount, company_currency_id,
                                                               pdc_payment.company_id, pdc_payment.deposit_date)
                else:
                    balance = pdc_payment.amount

                if pdc_payment.payment_type == "inbound":
                    pdc_credit_account_id = account_id
                    pdc_debit_account_id = customer_pdc_payment_account_id.id
                else:
                    pdc_credit_account_id = vendor_pdc_payment_account_id.id
                    pdc_debit_account_id = account_id

                if pdc_payment.company_id.currency_id != pdc_payment.currency_id:
                    amount_currency = pdc_payment.amount
                else:
                    amount_currency = balance

                currency = pdc_payment.journal_id.currency_id or pdc_payment.currency_id

                move_lines = [
                    (0, 0, pdc_payment._prepare_move_line(pdc_payment.deposit_date, pdc_debit_account_id, currency,
                                                          amount_currency, debit=balance)),
                    (0, 0, pdc_payment._prepare_move_line(pdc_payment.deposit_date, pdc_credit_account_id, currency,
                                                          -amount_currency, credit=balance))
                ]

                move = account_move_obj.create(pdc_payment._prepare_journal_entry(pdc_payment.deposit_date, move_lines,
                                                                                  currency))
                move.action_post()

                domain = [('account_type', 'in', ('asset_receivable', 'liability_payable')), ('reconciled', '=', False)]
                lines = move.line_ids
                inv_lines = invoices.line_ids.filtered_domain(domain)
                for account in inv_lines.account_id:
                    (inv_lines + lines).filtered_domain(
                        [("account_id", "=", account.id),
                         ("reconciled", "=", False)]).reconcile()

                vals = {"state": "deposit"}
                if pdc_payment.state == "register":
                    vals.update({"registered_deposit_entry": move.id})

                pdc_payment.write(vals)

    def action_done(self):
        # Get necessary models and parameters
        account_move_obj = self.env["account.move"]

        # Get configuration parameters

        # Loop through PDC payments
        for pdc_payment in self.filtered(lambda p: p.state in ["deposit"]):
            if not pdc_payment.collection_date:
                raise UserError(_("Collection Date is required."))
            # Check if necessary accounts are defined
            customer_pdc_payment_account_id = pdc_payment.company_id.customer_pdc_payment_account_id
            vendor_pdc_payment_account_id = pdc_payment.company_id.vendor_pdc_payment_account_id
            enable_deposit_entry = pdc_payment.enable_deposit_entry
            if customer_pdc_payment_account_id and vendor_pdc_payment_account_id:
                # Initialize variables
                debit_account = False
                credit_account = False

                # Check if deposit entry is enabled and if payment type is outbound
                if not enable_deposit_entry and pdc_payment.payment_type == "outbound":
                    # Check for required bank journal
                    if not pdc_payment.deposit_journal_id and not self.env.context.get('deposit_journal_id', False):
                        raise UserError(_("Please assign a bank journal as it is necessary at this stage."))

                    # Determine debit and credit accounts
                    debit_account = pdc_payment.journal_id.default_account_id.id
                    credit_account = pdc_payment.deposit_journal_id.default_account_id.id or self.env.context.get(
                        'deposit_journal_id', False).default_account_id.id
                    if not pdc_payment.deposit_journal_id:
                        pdc_payment.deposit_journal_id = self.env.context.get('deposit_journal_id', False)

                # Convert amount to company currency if necessary
                company_currency_id = pdc_payment.company_id.currency_id
                if pdc_payment.currency_id != company_currency_id:
                    balance = pdc_payment.currency_id._convert(pdc_payment.amount, company_currency_id,
                                                               pdc_payment.company_id, pdc_payment.collection_date)
                else:
                    balance = pdc_payment.amount
                if enable_deposit_entry:
                    credit_account = customer_pdc_payment_account_id.id
                else:
                    debit_account = pdc_payment.journal_id.default_account_id.id
                # Determine account IDs based on payment type
                if pdc_payment.payment_type == "inbound":
                    pdc_debit_account_id = pdc_payment.deposit_journal_id.default_account_id.id or debit_account
                    pdc_credit_account_id = credit_account or pdc_payment.journal_id.default_account_id.id
                else:
                    pdc_debit_account_id = debit_account or vendor_pdc_payment_account_id.id
                    pdc_credit_account_id = pdc_payment.deposit_journal_id.default_account_id.id or credit_account

                # Determine amount currency
                if pdc_payment.company_id.currency_id != pdc_payment.currency_id:
                    amount_currency = pdc_payment.amount
                else:
                    amount_currency = balance

                currency = pdc_payment.journal_id.currency_id or pdc_payment.currency_id

                # Prepare move lines
                move_lines = []
                move_lines.append((0, 0,
                                   pdc_payment._prepare_move_line(pdc_payment.collection_date, pdc_debit_account_id,
                                                                  currency, amount_currency, debit=balance)))
                move_lines.append((0, 0,
                                   pdc_payment._prepare_move_line(pdc_payment.collection_date, pdc_credit_account_id,
                                                                  currency, -amount_currency, credit=balance)))

                # Create and post accounting entries
                move = account_move_obj.create(
                    pdc_payment._prepare_journal_entry(pdc_payment.collection_date, move_lines, currency))
                move.action_post()

                # Update PDC payment state
                pdc_payment.write({"state": "done"})
            else:
                # Raise error if necessary accounts are not defined
                raise UserError(_("Configuration Error: Please define accounts for PDC payments."))

    def action_reset_to_draft(self):
        # Loop through PDC payments
        for pdc_payment in self.filtered(lambda p: p.state != 'draft'):
            # Update PDC payment state
            pdc_payment.write({"state": "draft"})
            entries = self.env['account.move'].search([('pdc_ref_id', '=', pdc_payment.id)])
            entries.button_draft()
            entries.button_cancel()

    def action_bounce(self):
        account_move_reversal_obj = self.env["account.move.reversal"]
        account_move_obj = self.env["account.move"]

        for pdc_payment in self.filtered(lambda p: p.state == "deposit"):
            # Check if bounce date is provided
            if not pdc_payment.bounce_date:
                raise UserError(_("Bounce Date is required."))

            # Check if registered deposit entry is available
            if pdc_payment.registered_deposit_entry:
                # Reverse the registered entry
                reversed_entry_wizard = account_move_reversal_obj.with_context(
                    active_model="account.move", active_ids=self.registered_deposit_entry.ids).create({
                    "date": pdc_payment.bounce_date,
                    "reason": "Reverse Entry",
                    "journal_id": pdc_payment.journal_id.id,
                })

                # Execute the reversal
                res = reversed_entry_wizard.reverse_moves()
                reversed_entry = account_move_obj.browse(res["res_id"])
                reversed_entry.pdc_ref_id = pdc_payment.id

                # Update PDC payment state
            pdc_payment.write({"state": "bounce"})

    def action_get_journal_entries(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("PDC Entries"),
            "res_model": "account.move",
            "view_mode": "form",
            "domain": [("pdc_ref_id", "=", self.id), ("move_type", "=", "entry")],
            "views": [(self.env.ref("account.view_move_tree").id, "list"), (False, "form")],
        }

    def action_get_invoices(self):
        action = self.sudo().env.ref("account.action_move_out_invoice_type")
        result = action.read()[0]
        result["domain"] = [("id", "in", self.invoice_ids.filtered(lambda inv: inv.move_type == "out_invoice").ids)]

        return result

    def action_get_bills(self):
        action = self.sudo().env.ref("account.action_move_in_invoice_type")
        result = action.read()[0]
        result["domain"] = [("id", "in", self.invoice_ids.filtered(lambda inv: inv.move_type == "in_invoice").ids)]

        return result
