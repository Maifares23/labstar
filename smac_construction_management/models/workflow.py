# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Workflow(models.Model):
    _name = 'workflow'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'
    _description = 'Workflow'

    name = fields.Char(string='Name',tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    construction_project_id = fields.Many2one(comodel_name="construction.project", string="Project", required=False, )
    stage_ids = fields.Many2many(comodel_name="stage", string="Stages", required=False, )
    model_id = fields.Many2one(comodel_name="ir.model", string="Model", required=False, )


    # @api.onchange('stage_ids')
    # def _onchange_stage_ids(self):
    #     for rec in self:
    #         for line in rec.stage_ids:
    #             line.workflow_id = rec.id
    #


