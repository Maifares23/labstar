# -*- coding: utf-8 -*-

from datetime import timedelta, datetime, date
import calendar

from odoo import fields, models, api, _


class ResCompany(models.Model):
    _name = "res.company"
    _inherit = ["res.company", "mail.thread"]

    customer_pdc_payment_account_id = fields.Many2one("account.account", string="PDC Payment Account for Customer",
                                                      company_dependent=True
                                                      )
    vendor_pdc_payment_account_id = fields.Many2one("account.account",
                                                    string="PDC Payment Account for Vendors/Suppliers",
                                                    company_dependent=True)
    enable_deposit_entry = fields.Boolean(string="Enable Deposit Entry", company_dependent=True)
