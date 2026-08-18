# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    pdc_type = fields.Selection([
        ("pdc_received", "PDC Received"),
        ("pdc_issued", "PDC Issued")
    ], string="PDC Type", tracking=True, index=True)
