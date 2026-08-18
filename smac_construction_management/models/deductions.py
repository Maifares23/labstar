# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta





class DeductionsLine(models.Model):
    _name = 'deductions.line'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Deductions Line'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)

    name = fields.Char(string="Description", required=False, )

    work_type = fields.Selection(string="Major work Type", selection=[('supply', 'Supply'),
                                                                      ('apply', 'Apply'),
                                                                      ('equ', 'Equipment Rental'),
                                                                      ('eng', 'Engineering Rental'),
                                                                      ('manpower', 'ManPower Rental')
                                                                      ], required=False, tracking=True)
    wbs_id = fields.Many2one(comodel_name="wbs", string="Wbs", required=False, )
    work_package_id = fields.Many2one(comodel_name="work.package", string="Work Package", required=False, )
    uom_id = fields.Many2one(comodel_name="uom.uom", string="Uom", required=False, )
    quantity = fields.Float(string="Quantity", required=False, )
    unit_price = fields.Float(string="Unit Price", required=False, )
    admin_fees = fields.Float(string="Admin Fees %", required=False, )
    reserved_unit_price = fields.Float(string="Reserved Unit Price", required=False,compute='get_amount' )
    amount = fields.Float(string="Amount", required=False,compute='get_amount' )

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    deduction_id = fields.Many2one(comodel_name="deductions", string="", required=False, )

    @api.depends('quantity','unit_price','admin_fees','reserved_unit_price')
    def get_amount(self):
        for rec in self:
            rec.reserved_unit_price = ((rec.unit_price * rec.admin_fees / 100) + rec.unit_price) if rec.admin_fees else rec.unit_price
            rec.amount = rec.quantity * rec.reserved_unit_price










class Deductions(models.Model):
    _name = 'deductions'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Deductions'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    name = fields.Char(string='Name', tracking=True, required=True)
    code = fields.Char(string='Code', tracking=True)
    project_id = fields.Many2one(comodel_name="construction.project", string="Project", required=False, tracking=True)
    subcontractor_id = fields.Many2one(comodel_name="res.partner", string="Subcontractor", required=False,
                                       tracking=True)
    contract_project_id = fields.Many2one(comodel_name="contract.project", string="Contract", required=False, )

    state = fields.Selection(string="State", selection=[('draft', 'Draft'), ('confirm', 'Confirm'), ], required=False,
                             default='draft')
    deduction_ids = fields.One2many(comodel_name="deductions.line", inverse_name="deduction_id", string="", required=False, )

    total_amount = fields.Float(string="Total Amount",  required=False,compute='get_total_amount')
    #workflow
    stage_id = fields.Many2one(comodel_name="stage", string="Stage", required=False,domain="[('workflow_id', '=', workflow_id)]" )
    workflow_id = fields.Many2one(comodel_name="workflow", string="Workflow", required=True )
    is_hide_confirm = fields.Boolean(string="Hide Confirm",  )
    is_confirm_invoice = fields.Boolean(string="Confirm Invoice",  )
    date_confirm_stage = fields.Date(string="Date Confirm Stage", required=False, )
    due_days = fields.Integer(string="Due Days", required=False, related='stage_id.due_days')
    num_days = fields.Date(string="Num Days", required=False, )
    ##############################33

    def send_notification_late(self):
        for rec in self:
            body = '<a target=_BLANK href="/web?#id=' + str(
                rec.id) + '&view_type=form&model=deductions&action=" style="font-weight: bold">' + str(
                rec.name) + '</a>'

            partners = [x.partner_id.id for x in rec.stage_id.mapped('group_ids').mapped('users')]
            partners_mangers = [x.partner_id.id for x in rec.stage_id.mapped('group_ids').mapped('users').mapped('managers_ids')]
            partners.extend(partners_mangers)
            print('partners',partners)
            partners = list(set(partners))
            print('partners', partners)
            # partners = [rec.project_id.user_id.partner_id.id]
            if partners:
                thread_pool = self.env['mail.thread']
                thread_pool.sudo().message_notify(
                    partner_ids=partners,
                    subject="Form " + str(rec.name) + " You Should Approve This Transaction",
                    body="Message:Form  " + str(body) + " You Should Approve This Transaction",
                    email_from=self.env.user.company_id.email)
    ##############################33

    @api.onchange('workflow_id')
    def get_stage_id(self):
        for rec in self:
            rec.stage_id = False

    def action_confirm(self):
        for rec in self:
            stage_all=self.env['stage'].sudo().search([('workflow_id', '=', rec.workflow_id.id)], order='sequence')
            if not rec.stage_id:
                stage=self.env['stage'].sudo().search([('workflow_id', '=', rec.workflow_id.id)],limit=1, order='sequence')
                print('stage',stage)
                if not stage:
                    raise UserError('No approval stages are configured for the selected workflow.')
                if self.env.user.id not in stage.group_ids.users.ids:
                    raise UserError('You Cannot Confirm.')
                else:
                    rec.stage_id = stage.id
                    rec.date_confirm_stage = fields.Date.today()
                    rec.num_days = rec.date_confirm_stage + timedelta(days=rec.due_days)
                    ########################
            else:
                stage = self.env['stage'].sudo().search([('sequence', '>', rec.stage_id.sequence),('id', 'in', stage_all.ids)], limit=1,order='sequence')
                if stage:
                    if self.env.user.id not in stage.group_ids.users.ids:
                        raise UserError('You Cannot Confirm.')
                    else:
                        rec.stage_id = stage.id
                        rec.date_confirm_stage = fields.Date.today()
                        rec.num_days = rec.date_confirm_stage + timedelta(days=rec.due_days)
                else:
                    rec.is_hide_confirm = True



    @api.depends('deduction_ids','deduction_ids.amount')
    def get_total_amount(self):
        for rec in self:
            rec.total_amount = sum(rec.deduction_ids.mapped('amount'))


    # def action_confirm(self):
    #     self.state = 'confirm'





