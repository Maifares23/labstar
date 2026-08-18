# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WorkPackage(models.Model):
    _name = 'work.package'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'
    _description = 'Work Package'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    name = fields.Char(string='Name',tracking=True)
    code = fields.Char(string='Code',tracking=True)
    project_id = fields.Many2one(comodel_name="construction.project", string="Project", required=False, tracking=True)
