# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'



    is_subcontractor = fields.Boolean(string="Is Subcontractor",  )
