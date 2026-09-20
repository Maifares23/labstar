# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    footer_bank_account_id = fields.Many2one(
        "res.partner.bank",
        string="Bank Account for Report Footer",
        domain="[('partner_id', '=', partner_id)]",
    )
    show_bank_footer_on_sale_order = fields.Boolean(
        string="Show Bank Details on Sale Orders",
    )
    show_bank_footer_on_invoice = fields.Boolean(
        string="Show Bank Details on Invoices",
    )
