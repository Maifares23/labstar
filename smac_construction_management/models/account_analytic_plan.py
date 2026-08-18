from odoo import api, fields, models


class AccountAnalyticPlan(models.Model):
    _inherit = 'account.analytic.plan'

    business_unit_id = fields.Many2one(comodel_name="business.unit", string="Business Unit")
