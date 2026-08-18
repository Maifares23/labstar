# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    journal_id = fields.Many2one(
        domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash')),('pdc_type','=',False)]")
