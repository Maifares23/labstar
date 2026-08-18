# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    pdc_id = fields.Many2one("pdc.payment", string="Post Dated Cheques", readonly=True, copy=False)
    pdc_ref_id = fields.Many2one("pdc.payment", string="Post Dated Cheques", readonly=True, copy=False)
    pdc_payments_count = fields.Integer(compute="_compute_pdc_payments_count", string="PDC Payments Count")
    batch_pdc_payments_count = fields.Integer(compute="_compute_pdc_payments_count", string="Batch PDC Payments Count")

    def _compute_pdc_payments_count(self):
        pdc_payment_obj = self.env["pdc.payment"]
        for move in self:
            pdc_payments = pdc_payment_obj.search([("invoice_ids", "in", move.ids)])
            move.pdc_payments_count = len(pdc_payments)
            move.batch_pdc_payments_count = len(pdc_payments.mapped("batch_id"))

    def action_get_pdc_payments(self):
        """
        Fetch the appropriate PDC payment action based on the move type and apply a domain filter
        for related invoices.
        """
        # Define mapping of move types to actions
        action_mapping = {
            'out_invoice': "pdc_cheques.action_pdc_payment_customer",
            'out_refund': "pdc_cheques.action_pdc_payment_customer",
            'in_invoice': "pdc_cheques.action_pdc_payment_vendor",
            'in_refund': "pdc_cheques.action_pdc_payment_vendor",
        }

        # Get the action reference based on the move type
        action_ref = action_mapping.get(self.move_type)
        if not action_ref:
            raise UserError(_("Unsupported move type: %s") % self.move_type)

        # Fetch and configure the action
        action = self.sudo().env.ref(action_ref)
        if not action:
            raise UserError(_("Unable to find the action for move type: %s") % self.move_type)

        result = action.read()[0]
        result["domain"] = [("invoice_ids", "in", self.ids)]
        return result

    def action_get_batch_pdc_payments(self):
        action = self.sudo().env.ref("pdc_cheques.action_pdc_payment_batch")
        result = action.read()[0]

        result["domain"] = [
            ("id", "in", self.env["pdc.payment"].search([("invoice_ids", "in", self.ids)]).mapped("batch_id").ids)]
        return result

    def js_assign_outstanding_line(self, line_id):
        res = super(AccountMove, self).js_assign_outstanding_line(line_id)

        lines = self.env["account.move.line"].browse(line_id)
        pdc_payments = lines.mapped("move_id.pdc_ref_id")
        if pdc_payments:
            pdc_payments.write({"invoice_ids": [(4, self.id)]})
        return res

    def js_remove_outstanding_partial(self, partial_id):
        if self.pdc_ref_id:
            partial = self.env["account.partial.reconcile"].browse(partial_id)
            debit_move = partial.debit_move_id.move_id
            credit_move = partial.credit_move_id.move_id
            if debit_move.is_invoice(include_receipts=True) and debit_move.id in self.pdc_ref_id.invoice_ids.ids:
                self.pdc_ref_id.write({"invoice_ids": [(3, debit_move.id)]})

            if credit_move.is_invoice(include_receipts=True) and credit_move.id in self.pdc_ref_id.invoice_ids.ids:
                self.pdc_ref_id.write({"invoice_ids": [(3, credit_move.id)]})

        return super(AccountMove, self).js_remove_outstanding_partial(partial_id)

    def button_draft(self):
        super(AccountMove, self).button_draft()

        for move in self:
            if move.is_invoice(include_receipts=True):
                pdc_payments = self.env["pdc.payment"].search([("invoice_ids", "in", [move.id])])
                if pdc_payments:
                    pdc_payments.write({"invoice_ids": [(3, move.id)]})


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    pdc_id = fields.Many2one("pdc.payment", string="Post Dated Cheques", copy=False, readonly=True)
