from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RentalContractLine(models.Model):
    _inherit = 'rental.contract.line'

    company_id = fields.Many2one('res.company', 'Company', related="rental_contract_id.company_id", store=True)
    brokerage_fee = fields.Float(
        string='Brokerage Fee (Not included in total contract amount)',
        required=False, related="rental_contract_id.brokerage_fee", store=True)
    security_deposit = fields.Float(
        string='Security Deposit (Not included in total contract amount)',
        required=False, related="rental_contract_id.security_deposit", store=True)
    waste_removal_fee = fields.Float(
        string='Waste Removal Fee (Not included in total contract amount)',
        required=False, related="rental_contract_id.waste_removal_fee", store=True)
    engineering_supervision_fee = fields.Float(
        string='Engineering Supervision Fee (Not included in total contract amount)',
        required=False, related="rental_contract_id.engineering_supervision_fee", store=True)
    unit_finishing_fee = fields.Float(
        string='Unit Finishing Fee (Not included in total contract amount)',
        required=False, related="rental_contract_id.unit_finishing_fee", store=True)
    retainer_fee = fields.Float(
        string='Retainer Fee (Included in total contract amount)',
        required=False, related="rental_contract_id.retainer_fee", store=True)

    gas_annual_mount = fields.Float(
        string='Gas Annual Amount',
        required=False, related="rental_contract_id.gas_annual_mount", store=True)
    electricity_annual_mount = fields.Float(
        string='Electricity Annual Amount',
        required=False, related="rental_contract_id.electricity_annual_mount", store=True)
    water_annual_mount = fields.Float(
        string='Water Annual Amount',
        required=False, related="rental_contract_id.water_annual_mount", store=True)
    general_services_mount = fields.Float(
        string='General Services Amount',
        required=False, related="rental_contract_id.general_services_mount", store=True)
    rental_value = fields.Float(
        string='Rental Value',
        required=False, related="rental_contract_id.rental_value", store=True)
    tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Vat',
        required=False)
    amount_with_tax = fields.Float(
        string='Amount With Vat',
        required=False)

    def make_invoice(self):
        res = super().make_invoice()
        move = self.env['account.move'].sudo().search([('rental_line_id', '=', self.id)])
        if move:
            analytic_account=self.rental_contract_id.analytic_account_id
            move.sudo().invoice_line_ids.update({
                'tax_ids': [(4, self.rental_contract_id.tax_id.id)] if self.rental_contract_id.tax_id else False,
                'analytic_distribution':{analytic_account.id: 100.0} if analytic_account else False
            })
            move.sudo().invoice_date = self.date
        return res

    def unlink(self):
        if self.rental_contract_id.state == 'confirmed':
            raise ValidationError(_("You can't delete"))
        return super().unlink()

    def paid_down_payment(self):
        down_payment_id = self.rental_contract_id.contract_down_payment_id
        if down_payment_id:
            invoice_id = self.invoice_id
            amount = 0
            if down_payment_id.remaining_amount > invoice_id.amount_residual:
                amount = invoice_id.amount_residual
            if down_payment_id.remaining_amount < invoice_id.amount_residual:
                amount = down_payment_id.remaining_amount
            tax_id= self.env.company.discount_invoice_tax_id
            if amount > 0:
                account_id = self.env.company.rental_account_id
                if not account_id:
                    raise ValidationError(_("Please Set Rental Deposit Account"))
                down_payment = [(0, 0, {
                    'account_id': account_id.id,
                    'name': _("Down payment"),
                    'tax_ids': [(4, tax_id.id)] if tax_id else False,
                    'quantity': 1,
                    'price_unit': - amount,
                })]
                invoice_id.sudo().invoice_line_ids = down_payment
                down_payment_id.paid_amount += amount
                down_payment_id.remaining_amount -= amount
                if down_payment_id.paid_amount > 0 and down_payment_id.paid_amount != down_payment_id.amount:
                    down_payment_id.contract_state = 'reserved'
                if down_payment_id.paid_amount == down_payment_id.amount:
                    down_payment_id.contract_state = 'closed'
