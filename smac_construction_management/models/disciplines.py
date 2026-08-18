# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Disciplines(models.Model):
    _name = 'disciplines'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'
    _description = 'Disciplines'


    name = fields.Char(string='Name',tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
