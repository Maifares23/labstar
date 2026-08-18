# -*- coding: utf-8 -*-

from odoo import api, fields, models


class BusinessUnit(models.Model):
    _name = 'business.unit'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'
    _description = 'Business Unit'

    name = fields.Char(string='Name', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    manager_id = fields.Many2one('res.users', string='Manager', tracking=True)
    project_id = fields.Many2one('construction.project', string='Project', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            self.env['account.analytic.plan'].create({
                'name': record.name or record.display_name,
                'business_unit_id': record.id,
            })
        return records
