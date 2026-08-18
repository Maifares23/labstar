# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'



    managers_ids = fields.Many2many(comodel_name="res.users", relation="managers_ids", column1="managers", column2="managers_2", string="Managers", )
