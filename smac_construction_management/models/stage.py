# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StageRequest(models.Model):
    _name = 'stage.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'
    _description = 'Stage Request'

    name = fields.Char(string='Name',tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    group_ids = fields.Many2many(comodel_name="res.groups",  string="Groups",required=True )
    sequence = fields.Integer(string="Sequence", required=False, )
    construction_project_id = fields.Many2one(comodel_name="construction.project", string="Project", required=False, )





class StageContract(models.Model):
    _name = 'stage.contract'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'
    _description = 'Stage Contract'

    name = fields.Char(string='Name',tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    group_ids = fields.Many2many(comodel_name="res.groups",  string="Groups",required=True )
    sequence = fields.Integer(string="Sequence", required=False, )
    construction_project_id = fields.Many2one(comodel_name="construction.project", string="Project", required=False, )




class StageDeductions(models.Model):
    _name = 'stage.deductions'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'
    _description = 'Stage Deductions'

    name = fields.Char(string='Name',tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    group_ids = fields.Many2many(comodel_name="res.groups",  string="Groups",required=True )
    sequence = fields.Integer(string="Sequence", required=False, )
    construction_project_id = fields.Many2one(comodel_name="construction.project", string="Project", required=False, )






class StageInvoice(models.Model):
    _name = 'stage.invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'
    _description = 'StageInvoice'

    name = fields.Char(string='Name',tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    group_ids = fields.Many2many(comodel_name="res.groups",  string="Groups",required=True )
    sequence = fields.Integer(string="Sequence", required=False, )
    construction_project_id = fields.Many2one(comodel_name="construction.project", string="Project", required=False, )





class Stage(models.Model):
    _name = 'stage'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'
    _description = 'Stages'
    _order = 'sequence, id'

    name = fields.Char(string='Name',tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    group_ids = fields.Many2many(comodel_name="res.groups",  string="Groups",required=True )
    sequence = fields.Integer(string="Sequence", required=False, )
    change_request_id = fields.Many2one(comodel_name="change.request.project", string="Change Request", required=False, )
    contract_invoice_id = fields.Many2one(comodel_name="contract.invoice", string="invoice", required=False, )
    contract_project_id = fields.Many2one(comodel_name="contract.project", string="Contract", required=False, )
    deductions_id = fields.Many2one(comodel_name="deductions", string="Deductions", required=False, )
    construction_project_id = fields.Many2one(comodel_name="construction.project", string="Project", required=False, )
    workflow_id = fields.Many2one(comodel_name="workflow", string="Workflow", required=False)
    due_days = fields.Integer(string="Due Days", required=False, )




