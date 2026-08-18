# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ContractDownPayment(models.Model):
    _name = 'contract.down.payment'
    _description = 'Contract Down Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Reference", readonly=True, copy=False, default="New")
    memo = fields.Char(string="Memo")
    partner_id = fields.Many2one('res.partner', string="Customer", required=True, tracking=True)
    contract_id = fields.Many2one('rental.contract', string="Rental Contract", tracking=True)
    amount = fields.Float(string="Amount", required=True, tracking=True)
    tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Vat',
        required=False)

    date = fields.Date(
        string='Date',
        required=False, default=fields.Date.context_today)
    journal_id = fields.Many2one(
        'account.journal', string="Payment Journal",
        domain=[('type', 'in', ('bank', 'cash'))],
        required=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], default='draft', tracking=True)
    contract_state = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('closed', 'Closed')
    ], default='available', string="Contract State", tracking=True)
    paid_amount = fields.Float(string="Paid Amount", tracking=True)
    remaining_amount = fields.Float(string="Remaining Amount", tracking=True)

    invoice_id = fields.Many2one('account.move', string="Invoice", readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('contract.down.payment') or 'New'
        return super().create(vals)

    def action_confirm(self):
        for rec in self:
            account_id = self.env.company.rental_account_id
            if not account_id:
                raise ValidationError(_("Please Set Rental Deposit Account"))
            move_vals = {
                'move_type': 'out_invoice',
                'partner_id': rec.partner_id.id,
                'invoice_date': rec.date,
                'invoice_date_due': rec.date,
                'contract_down_payment_id': rec.id,
                'invoice_line_ids': [(0, 0, {
                    'name': 'Down Payment',
                    'quantity': 1,
                    'price_unit': rec.amount,
                    'tax_ids': [(4, rec.tax_id.id)] if rec.tax_id else False,
                    'account_id': account_id.id,
                })],
            }
            invoice = self.env['account.move'].create(move_vals)
            invoice.action_post()
            payment_register = self.env['account.payment.register'].with_context(
                active_model='account.move', active_ids=invoice.ids
            ).create({
                'journal_id': rec.journal_id.id,
                'amount': rec.amount,
                'communication': rec.memo,
                'payment_date': rec.date,
            })
            payment_register._create_payments()
            rec.invoice_id = invoice.id
            rec.remaining_amount = rec.amount
            rec.state = 'done'

    def create_credit_note(self):
        for rec in self:
            account_id = self.env.company.rental_account_id
            if not account_id:
                raise ValidationError(_("Please Set Rental Deposit Account"))
            move_vals = {
                'move_type': 'out_refund',
                'partner_id': rec.partner_id.id,
                'contract_down_payment_id': rec.id,
                'invoice_line_ids': [(0, 0, {
                    'name': 'Down Payment',
                    'quantity': 1,
                    'price_unit': rec.remaining_amount,
                    'account_id': account_id.id,
                })],
            }
            credit_note = self.env['account.move'].create(move_vals)
            credit_note.action_post()
            payment_register = self.env['account.payment.register'].with_context(
                active_model='account.move', active_ids=credit_note.ids
            ).create({
                'journal_id': rec.journal_id.id,
                'amount': rec.amount,
                'communication': rec.memo,
                'payment_date': rec.date,
            })
            payment_register._create_payments()
            for payment in credit_note.matched_payment_ids:
                payment.action_validate()
            rec.remaining_amount = 0
            rec.state = 'done'
            rec.contract_state = 'closed'
            return credit_note

    def action_cancel(self):
        self.state = 'cancel'

    def action_view_invoice(self):
        """Smart Button: عرض الفاتورة"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'views': [(False, 'list'), (False, 'form')],
            'domain': [('contract_down_payment_id', '=', self.id)],
        }

    def unlink(self):
        state = self.state
        result = super().unlink()
        if state == 'done':
            raise ValidationError("You Can't Delete")
        return result
