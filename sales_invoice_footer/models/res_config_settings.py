# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    footer_bank_account_id = fields.Many2one(
        related="company_id.footer_bank_account_id", readonly=False,
    )
    show_bank_footer_on_sale_order = fields.Boolean(
        related="company_id.show_bank_footer_on_sale_order", readonly=False,
    )
    show_bank_footer_on_invoice = fields.Boolean(
        related="company_id.show_bank_footer_on_invoice", readonly=False,
    )
