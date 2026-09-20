# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    iban_number = fields.Char(
        string="IBAN Number",
        help="International Bank Account Number to print in the report footer, "
        "used when it is different from the Account Number.",
    )
