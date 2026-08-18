# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models

from odoo.exceptions import UserError, ValidationError


class PdcPaymentWizard(models.TransientModel):
    _name = 'pdc.payment.wizard'
    _description = 'Pdc Payment Wizard'

    invoice_ids = fields.Many2many(
        'account.move', string="Invoices", copy=False, readonly=True
    )
    partner_id = fields.Many2one(
        'res.partner', string='Partner', required=True, copy=False)
    move_type = fields.Selection(related="invoice_ids.move_type", store=True)
    available_journal_ids = fields.Many2many('account.journal', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain="[('id', 'in', available_journal_ids)]")
    company_id = fields.Many2one(
        'res.company', related='journal_id.company_id', string='Company', readonly=True
    )
    residual_amount = fields.Monetary(readonly=True)
    communication = fields.Char(string='Memo')
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id
    )
    payment_type = fields.Selection(
        [('outbound', 'Send Money'), ('inbound', 'Receive Money')], string='Payment Type', required=True,
    )
    line_ids = fields.One2many("pdc.payment.wizard.line", 'wizard_id', domain=[("batch_pdc", "=", False)])
    batch_line_ids = fields.One2many("pdc.payment.wizard.line", 'wizard_id', domain=[("batch_pdc", "=", True)])
    batch_pdc = fields.Boolean('Batch PDC')
    amount = fields.Monetary(string='Total Amount')
    cheques_no = fields.Integer(string="Total No of Cheques", default="1")
    no_of_months = fields.Integer(string="No of months", default="1")

    first_cheque_date = fields.Date(string='First Cheque Date', default=fields.Date.context_today)
    first_cheque_ref = fields.Char('First Cheque Ref')
    deposit_journal_id = fields.Many2one(comodel_name="account.journal", string="Bank Journal",
                                         domain=[('type', 'in', ['bank']), ('pdc_type', '=', False)])

    @api.constrains("first_cheque_ref", "batch_pdc")
    def _check_first_cheque_ref(self):
        for pdc_payment_wizard in self.filtered(lambda p: p.batch_pdc and p.first_cheque_ref):
            if not pdc_payment_wizard.first_cheque_ref.isdigit():
                raise ValidationError(
                    _("The first cheque ref %s must be a sequence of digits." % pdc_payment_wizard.first_cheque_ref))

    @api.model
    def default_get(self, default_fields):
        rec = super(PdcPaymentWizard, self).default_get(default_fields)
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
        amount = sum(invoices.mapped('amount_residual'))

        payment_type = 'inbound' if dtype in ['out_invoice', 'in_refund'] else 'outbound'

        if payment_type == "inbound":
            domain = [("pdc_type", "=", "pdc_received")]
        else:
            domain = [("pdc_type", "=", "pdc_issued")]

        available_journal_ids = self.env["account.journal"].search(domain)
        rec.update({
            'currency_id': invoices[0].currency_id.id,
            'residual_amount': abs(amount),
            'amount': abs(amount),
            'payment_type': payment_type,
            'partner_id': invoices[0].commercial_partner_id.id,
            'communication': invoices[0].payment_reference or invoices[0].ref or invoices[0].name,
            'invoice_ids': [(6, 0, invoices.ids)],
            'available_journal_ids': [(6, 0, available_journal_ids.ids)]
        })
        return rec

    @api.onchange("batch_pdc")
    def onchange_line_ids(self):
        self.line_ids = False
        self.batch_line_ids = False
        self.first_cheque_ref = False
        self.cheques_no = 1
        self.no_of_months = 1

    def create_pdc_cheques(self):
        self.line_ids = False
        self.batch_line_ids = False

        cheque_ref = ""
        if self.batch_pdc:
            cheque_ref = int(self.first_cheque_ref)

        for n in range(0, self.cheques_no):
            self.env["pdc.payment.wizard.line"].sudo().create(
                {
                    "amount": self.amount / self.cheques_no,
                    "wizard_id": self.id,
                    "journal_id": self.journal_id.id,
                    "due_date": self.first_cheque_date + relativedelta(months=n * self.no_of_months),
                    "cheque_ref": self.batch_pdc and cheque_ref or False,
                    "communication": self.communication,
                    "batch_pdc": self.batch_pdc
                }
            )
            if self.batch_pdc:
                cheque_ref += 1

        return {
            'context': self.env.context,
            'name': 'Pdc Payment Wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pdc.payment.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def _prepare_pdc_batch_payment(self):
        vals = {
            "name": "New",
            "partner_id": self.partner_id.id,
            "journal_id": self.journal_id.id,
            "amount": self.amount,
            "currency_id": self.currency_id.id,
            "communication": self.communication,
            "cheques_no": self.cheques_no,
            "no_of_months": self.no_of_months,
            "first_cheque_date": self.first_cheque_date,
            "first_cheque_ref": self.first_cheque_ref,
            "payment_type": self.payment_type,
            "deposit_journal_id": self.deposit_journal_id.id or False
        }
        return vals

    def action_confirm(self):
        """Confirm the action by validating lines, creating PDC payments, and handling batch processing."""
        # Validate lines for cheque references
        lines = self.batch_line_ids if self.batch_pdc else self.line_ids
        if any(not line.cheque_ref for line in lines):
            raise UserError(_("Please ensure that a cheque reference for each line is provided."))

        # Initialize PDC batch payment if applicable
        pdc_batch_payment = False
        if self.batch_pdc and self.batch_line_ids:
            pdc_batch_payment = self.env["batch.pdc.payment"].create(self._prepare_pdc_batch_payment())

        # Determine PDC type based on invoice type
        vendor_pdc, customer_pdc = 0, 0
        if self.invoice_ids:
            invoice_type = self.invoice_ids[0].move_type
            if pdc_batch_payment:
                pdc_batch_payment.partner_type = 'customer' if invoice_type == 'out_invoice' else 'vendor'
            vendor_pdc = 1 if invoice_type == 'in_invoice' else 0
            customer_pdc = 1 if invoice_type == 'out_invoice' else 0

        # Prepare payment values
        payment_vals = [{
            'invoice_ids': [(6, 0, self.invoice_ids.ids)],
            'partner_id': self.partner_id.id,
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'amount': line.amount,
            'currency_id': self.currency_id.id,
            'payment_date': line.payment_date,
            'due_date': line.due_date,
            'communication': line.communication,
            'cheque_ref': line.cheque_ref,
            'agent': line.agent,
            'bank': line.bank.id,
            'name': line.name,
            'payment_type': self.payment_type,
            'batch_id': pdc_batch_payment.id if pdc_batch_payment else False,
            "deposit_journal_id": self.deposit_journal_id.id or False,
            "customer_pdc": customer_pdc,
            "vendor_pdc": vendor_pdc,
        } for line in lines]

        # Create PDC payments
        pdc_payments = self.env['pdc.payment'].create(payment_vals)

        # Lock the batch payment if created
        if pdc_batch_payment:
            pdc_batch_payment.state = 'lock'

        # Register the payments
        pdc_payments.action_register()


class PdcPaymentWizardLine(models.TransientModel):
    _name = 'pdc.payment.wizard.line'
    _description = 'Pdc Payment Wizard Line'

    amount = fields.Monetary(string='Payment Amount', required=True)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    due_date = fields.Date(string='Due Date', default=fields.Date.context_today, required=True, copy=False)
    cheque_ref = fields.Char('Cheque Reference')
    agent = fields.Char('Agent')
    bank = fields.Many2one('res.bank', string="Bank")
    name = fields.Char('Name')
    wizard_id = fields.Many2one('pdc.payment.wizard')
    communication = fields.Char(string='Memo')
    company_id = fields.Many2one(
        'res.company', related='journal_id.company_id', string='Company', readonly=True
    )

    journal_id = fields.Many2one(
        'account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ['bank'])])
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id
    )
    batch_pdc = fields.Boolean(string="Batch PDC")
