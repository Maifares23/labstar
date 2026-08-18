from odoo import api, fields, models


class OwnerShipContract(models.Model):
    _inherit = 'ownership.contract'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'
