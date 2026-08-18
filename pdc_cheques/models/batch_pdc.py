# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class BatchPdcPayment(models.Model):
    _name = "batch.pdc.payment"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', default='New', copy=False)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    state = fields.Selection([('draft', 'Draft'), ('lock', 'Locked')], readonly=True, default='draft', copy=False,
                             string="Status")
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain="[('type', 'in', ['bank']), ('pdc_type', '=', pdc_journal_type)]")

    deposit_journal_id = fields.Many2one('account.journal', string='Bank Journal',
                                         domain=[('type', 'in', ['bank']), ('pdc_type', '=', False)])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    communication = fields.Char(string='Memo')
    cheques_no = fields.Integer(string="Total No of Cheques", default="1")
    no_of_months = fields.Integer(string="No of months", default="1")
    first_cheque_date = fields.Date(string='First Cheque Date', default=fields.Date.context_today)
    first_cheque_ref = fields.Char('First Cheque Ref')

    agent = fields.Char('Agent')
    bank = fields.Many2one('res.bank', string="Bank")
    payment_type = fields.Selection([('inbound', 'Receive Money'), ('outbound', 'Send Money')], default='inbound',
                                    string='Payment Type', required=True)
    partner_type = fields.Selection([('customer', 'Customer'), ('vendor', 'Vendor')], default='customer',
                                    string='Partner Type', required=True)
    batch_pdc_line_ids = fields.One2many('batch.pdc.payment.line', 'batch_pdc_id', string='PDC Lines')

    @api.depends('payment_type')
    def _compute_pdc_journal_type(self):
        for rec in self:
            if rec.payment_type == 'outbound':
                rec.pdc_journal_type = 'pdc_issued'
            else:
                rec.pdc_journal_type = 'pdc_received'

    pdc_journal_type = fields.Selection([
        ('pdc_issued', 'PDC Issued'),
        ('pdc_received', 'PDC Received'),
    ], compute='_compute_pdc_journal_type', string='PDC Journal Type', store=True)

    @api.constrains("first_cheque_ref")
    def _check_first_cheque_ref(self):
        for batch_pdc_payment in self.filtered(lambda p: p.first_cheque_ref):
            if not batch_pdc_payment.first_cheque_ref.isdigit():
                raise ValidationError(
                    _("The first cheque ref %s must be a sequence of digits." % batch_pdc_payment.first_cheque_ref))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('batch.pdc.payment')
        return super(BatchPdcPayment, self).create(vals)

    def lock(self):
        if self.state != "draft":
            return

        # register cheques
        self.line_ids.action_register()

        self.state = 'lock'

    @api.ondelete(at_uninstall=False)
    def _unlink_except_done(self):
        if 'lock' in self.mapped('state'):
            raise UserError(_('You cannot delete a Batch PDC which is Locked.'))

    def _prepare_pdc_payment(self, cheque_ref, due_date, amount):
        return {
            "amount": amount,
            "batch_id": self.id,
            "journal_id": self.journal_id.id,
            "deposit_journal_id": self.deposit_journal_id.id,
            "payment_type": self.payment_type,
            "agent": self.agent,
            "partner_id": self.partner_id.id,
            "bank": self.bank.id,
            "due_date": due_date,
            "cheque_ref": cheque_ref,
            "communication": self.communication,
            "customer_pdc": 1 if self.partner_type == 'customer' else 0,
            "vendor_pdc": 1 if self.partner_type == 'vendor' else 0,
        }

    def action_compute_pdc_lines(self):
        for batch_pdc in self:
            batch_pdc.batch_pdc_line_ids.unlink()
            lines = []
            for cheque_number in range(0, batch_pdc.cheques_no):
                line_vals = {
                    'batch_pdc_id': batch_pdc.id,
                    'cheque_ref': batch_pdc.first_cheque_ref + str(cheque_number),
                    'due_date': batch_pdc.first_cheque_date + relativedelta(
                        months=cheque_number * batch_pdc.no_of_months),
                    'amount': batch_pdc.amount / batch_pdc.cheques_no,
                }
                lines.append((0, 0, line_vals))
            batch_pdc.batch_pdc_line_ids = lines

    def action_confirm_pdc_lines(self):
        pdc_payment = self.env["pdc.payment"]
        for batch_pdc in self:
            if batch_pdc.batch_pdc_line_ids:
                for pdc_line in batch_pdc.batch_pdc_line_ids:
                    pdc_id = pdc_payment.create(
                        batch_pdc._prepare_pdc_payment(pdc_line.cheque_ref, pdc_line.due_date, pdc_line.amount))
                    pdc_id.action_register()
                    pdc_line.pdc_id = pdc_id
        batch_pdc.state = 'lock'

    def generate_cheques(self):
        pdc_payment_obj = self.env["pdc.payment"].sudo()
        for batch_pdc in self:
            batch_pdc.line_ids = False

            cheque_ref = int(batch_pdc.first_cheque_ref)

            for cheque_number in range(0, batch_pdc.cheques_no):
                pdc_payment_obj.create(batch_pdc._prepare_pdc_payment(cheque_ref, cheque_number))

                if batch_pdc.first_cheque_ref:
                    cheque_ref += 1

        return True

    @api.onchange("journal_id")
    def onchange_journal(self):
        currency_id = False
        if self.journal_id:
            journal = self.journal_id
            currency_id = journal.currency_id or journal.company_id.currency_id or self.env.user.company_id.currency_id
            currency_id = currency_id.id

        self.currency_id = currency_id


class BatchPdcPaymentLine(models.Model):
    _name = "batch.pdc.payment.line"
    _description = "Batch PDC Payment Line"

    batch_pdc_id = fields.Many2one('batch.pdc.payment', string='Batch PDC Payment', required=True)
    pdc_id = fields.Many2one('pdc.payment', string='PDC Payment', readonly=True)
    cheque_ref = fields.Char(string='Cheque Reference', required=True)
    due_date = fields.Date(string='Due Date', required=True)
    amount = fields.Monetary(string='Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
