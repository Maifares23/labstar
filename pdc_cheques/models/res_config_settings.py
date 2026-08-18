# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    customer_pdc_payment_account_id = fields.Many2one(related="company_id.customer_pdc_payment_account_id",
                                                      string="PDC Payment Account for Customer",
                                                      readonly=False)
    vendor_pdc_payment_account_id = fields.Many2one(related="company_id.vendor_pdc_payment_account_id",
                                                    readonly=False,
                                                    string="PDC Payment Account for Vendors/Suppliers")
    enable_deposit_entry = fields.Boolean(related="company_id.enable_deposit_entry", string="Enable Deposit Entry",
                                          readonly=False)
