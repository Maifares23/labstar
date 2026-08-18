from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError


class InvoiceWizard(models.TransientModel):
    _name = 'invoice.wizard'
    _description = 'Delete Invoice'

    date = fields.Date(string="Date", required=False, default=datetime.today())

    def action_confirm(self):
        if not self.date:
            raise ValidationError(_("Set Date"))
        invoice_ids = self.env['account.move'].sudo().search(
            [('invoice_date', '<', self.date), ('move_type', '=', 'out_invoice')])
        for invoice in invoice_ids:
            print("!!!!!!!!!!!!!", invoice)
            if invoice.state == 'posted':
                invoice.sudo().button_draft()
            if invoice.state in ['draft', 'cancel']:
                invoice.sudo().unlink()
        # old_contract_lines = self.env['rental.contract.line'].sudo().search(
        #     [('date', '<', self.date)])
        # if old_contract_lines:
        #     for line in old_contract_lines:
        #         line.sudo().unlink()
