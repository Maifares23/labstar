# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import ValidationError, UserError


class PdcReconcileCollectionCheck(models.Model):
    _name = "pdc.reconcile.collection.check"
    _description = "Reconcile Collection Check"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Number", index=True, tracking=True, readonly=True)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True, index=True, tracking=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("confirm", "Confirmed")], string="Status", default="draft", index=True, required=True, readonly=True,
        tracking=True)
    check_collection_date = fields.Date(string="Check Collection Date", default=fields.Date.context_today,
                                        required=True, tracking=True)
    check_number = fields.Char(string="Check Number", required=True, tracking=True)
    deposit_journal_id = fields.Many2one('account.journal', string='Bank Journal',
                                         domain=[('type', 'in', ['bank']), ('pdc_type', '=', False)])

    def unlink(self):
        for reconcile_collection_check in self:
            if reconcile_collection_check.state != "draft":
                raise UserError(
                    _("You cannot delete reconcile collection check %s which is not draft") % reconcile_collection_check.name)

        return super(PdcReconcileCollectionCheck, self).unlink()

    def action_confirm(self):
        # Get necessary models
        ir_sequence_obj = self.env["ir.sequence"]
        pdc_payment_obj = self.env["pdc.payment"]

        # Loop through draft reconcile collection checks
        for reconcile_collection_check in self.filtered(lambda rc: rc.state == "draft"):
            # Search for corresponding PDC payment
            pdc_payment = pdc_payment_obj.search([
                ("state", "=", "deposit"),
                ("partner_id", "=", reconcile_collection_check.customer_id.id),
                ("cheque_ref", "=", reconcile_collection_check.check_number)
            ], limit=1)

            # Raise error if PDC payment not found
            if not pdc_payment:
                raise ValidationError(_("No PDC payment found for check number %s for customer %s" % (
                    reconcile_collection_check.check_number, reconcile_collection_check.customer_id.display_name)))

            # Set collection date for PDC payment and mark it as collected
            pdc_payment.write({"collection_date": reconcile_collection_check.check_collection_date})
            pdc_payment.with_context(deposit_journal_id=reconcile_collection_check.deposit_journal_id).action_done()

            # Update state and generate sequence for reconcile collection check
            reconcile_collection_check.write({
                "state": "confirm",
                "name": ir_sequence_obj.next_by_code("pdc.reconcile.collection.check")
            })
