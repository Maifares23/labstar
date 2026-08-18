# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta


class ChangeRequestProjectSubLine(models.Model):
    _name = 'change.request.project.sub.line'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Change Request Project SubLine'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    item_id = fields.Many2one(comodel_name="items", string="Items", required=False, )
    name = fields.Char(string='Name', tracking=True)
    work_type = fields.Selection(string="Major work Type", selection=[('supply', 'Supply'),
                                                                      ('apply', 'Apply'),
                                                                      ('equ', 'Equipment Rental'),
                                                                      ('eng', 'Engineering Rental'),
                                                                      ('manpower', 'ManPower Rental')
                                                                      ], required=False, tracking=True)
    work_package_id = fields.Many2one(comodel_name="work.package", string="Work Package", required=False, )
    quantity = fields.Float(string="Quantity", required=False, )
    unit_price = fields.Float(string="Unit Price", required=False, )
    uom_id = fields.Many2one(comodel_name="uom.uom", string="Uom", required=False, )
    tax_ids = fields.Many2many('account.tax', string="Taxes", tracking=True)
    untaxed_amount = fields.Float(string="Untaxed Amount", compute="get_total_before_discount",
                                  tracking=True)
    amount_tax = fields.Float(string="Amount Tax", compute="get_total_before_discount",
                              store=True, tracking=True)
    total_amount = fields.Float(string="Total Amount", compute="get_total_before_discount",
                                store=True, tracking=True)
    contract_line_id = fields.Many2one(comodel_name="change.request.project.line", string="change.request Line",
                                       required=False, )
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    contract_project_sub_line_id = fields.Many2one(comodel_name="contract.project.sub.line", string="",
                                                   required=False, )

    # total_amount = fields.Float(string="Total Amount", compute="get_total_before_discount",
    #                             tracking=True)

    @api.onchange('item_id')
    def get_name_item(self):
        for rec in self:
            rec.name = rec.item_id.name

    @api.depends('tax_ids', 'quantity', 'unit_price')
    def get_total_before_discount(self):
        for rec in self:
            untaxed_amount = rec.quantity * rec.unit_price
            taxes = rec.tax_ids.compute_all(untaxed_amount, self.env.user.company_id.currency_id, 1)
            rec.untaxed_amount = taxes['total_excluded']
            rec.amount_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            rec.total_amount = taxes['total_included']


class ChangeRequestProjectLine(models.Model):
    _name = 'change.request.project.line'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Change Request Project Line'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    item_id = fields.Many2one(comodel_name="items", string="Items", required=False, )
    name = fields.Char(string='Name', tracking=True)
    work_type = fields.Selection(string="Major work Type", selection=[('supply', 'Supply'),
                                                                      ('apply', 'Apply'),
                                                                      ('equ', 'Equipment Rental'),
                                                                      ('eng', 'Engineering Rental'),
                                                                      ('manpower', 'ManPower Rental')
                                                                      ], required=False, tracking=True)
    work_package_id = fields.Many2one(comodel_name="work.package", string="Work Package", required=False, )
    quantity = fields.Float(string="Quantity", required=False, default=1)
    unit_price = fields.Float(string="Unit Price", compute="get_total_before_discount",
                              store=True, tracking=True, readonly=False)
    uom_id = fields.Many2one(comodel_name="uom.uom", string="Uom", required=False, )
    tax_ids = fields.Many2many('account.tax', string="Taxes", tracking=True)
    untaxed_amount = fields.Float(string="Untaxed Amount", compute="get_total_before_discount",
                                  tracking=True)
    amount_tax = fields.Float(string="Amount Tax", compute="get_total_before_discount",
                              store=True, tracking=True)
    total_amount = fields.Float(string="Total Amount", compute="get_total_before_discount",
                                store=True, tracking=True)
    contract_project_id = fields.Many2one(comodel_name="change.request.project", string="Contract Project",
                                          required=False, )
    project_sub_line_ids = fields.One2many(comodel_name="change.request.project.sub.line",
                                           inverse_name="contract_line_id", string="", required=False, )
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    contract_project_line_id = fields.Many2one(comodel_name="contract.project.line", string="", required=False, )

    def view_sub_line_pop_up(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Items Lines',
                'res_model': 'change.request.project.line',
                'view_mode': 'form',
                'res_id': self.id,
                'domain': [('id', '=', rec.id), ('display_type', 'not in', ['line_section', 'line_note'])],
                # 'context': {'default_contract_line_id': rec.id},
                'target': 'new',
            }

    @api.onchange('item_id')
    def get_name_item(self):
        for rec in self:
            rec.name = rec.item_id.name

    @api.depends('tax_ids', 'project_sub_line_ids', 'quantity', 'unit_price')
    def get_total_before_discount(self):
        for rec in self:
            untaxed_amount = sum(rec.project_sub_line_ids.mapped(
                'untaxed_amount')) if rec.project_sub_line_ids else rec.quantity * rec.unit_price
            rec.unit_price = sum(rec.project_sub_line_ids.mapped('unit_price')) if rec.project_sub_line_ids else rec.unit_price
            taxes = rec.tax_ids.compute_all(untaxed_amount, self.env.user.company_id.currency_id, 1)
            rec.untaxed_amount = taxes['total_excluded']
            rec.amount_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            rec.total_amount = taxes['total_included']


class ChangeRequestProject(models.Model):
    _name = 'change.request.project'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Change Request Project'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    name = fields.Char(string='Name', tracking=True, required=True)
    code = fields.Char(string='Code', tracking=True)
    project_id = fields.Many2one(comodel_name="construction.project", string="Project", required=False, tracking=True)
    subcontractor_id = fields.Many2one(comodel_name="res.partner", string="Subcontractor", required=False,
                                       tracking=True)
    date_from = fields.Date(string="Date From", required=False, )
    date_to = fields.Date(string="Date To", required=False, )
    contract_project_ids = fields.One2many(comodel_name="change.request.project.line",
                                           inverse_name="contract_project_id",
                                           string="Items", required=False, tracking=True)
    work_type = fields.Selection(string="Major work Type", selection=[('supply', 'Supply'),
                                                                      ('apply', 'Apply'),
                                                                      ('equ', 'Equipment Rental'),
                                                                      ('eng', 'Engineering Rental'),
                                                                      ('manpower', 'ManPower Rental')
                                                                      ], required=False, tracking=True)
    disciplines_id = fields.Many2one(comodel_name="disciplines", string="Disciplines", required=False, tracking=True)
    description_custom = fields.Text(string='Work Description', translate=True, tracking=True)
    open_end_contract = fields.Boolean(string='Open End Contract', tracking=True)
    open_cost_contract = fields.Boolean(string='Open Cost Contract', tracking=True)
    contract_duration = fields.Integer(required=False, tracking=True)
    contract_payment_duration = fields.Integer(required=False, tracking=True)
    contract_date = fields.Datetime(string="Contract Date", required=False, tracking=True)
    advanced_payment_percentage = fields.Float(required=False, readonly=False, tracking=True)
    advanced_payment_amount = fields.Float(required=False, readonly=False, tracking=True)

    retention_payment_percentage = fields.Float(required=False, readonly=False, tracking=True)
    retention_payment_amount = fields.Float(required=False, readonly=False, tracking=True)

    state = fields.Selection(string="State", selection=[('draft', 'Draft'), ('confirm', 'Confirm'), ], required=False,
                             default='draft')
    contract_project_id = fields.Many2one(comodel_name="contract.project", string="Contract", required=False, )
    is_get_data = fields.Boolean(string="", default=False)
    is_time = fields.Boolean(string="Time", default=False)
    is_quantity = fields.Boolean(string="Quantity", default=False)
    is_price = fields.Boolean(string="Price", default=False)
    is_scope = fields.Boolean(string="Scope", default=False)
    is_other = fields.Boolean(string="Other", default=False)
    total_untaxed_amount = fields.Float(string="Total Untaxed Amount", compute="get_total_untaxed_amount",
                                  tracking=True)
    # workflow
    stage_id = fields.Many2one(comodel_name="stage", string="Stage", required=False,
                               domain="[('workflow_id', '=', workflow_id)]")
    workflow_id = fields.Many2one(comodel_name="workflow", string="Workflow", required=True)
    is_hide_confirm = fields.Boolean(string="Hide Confirm", )
    date_confirm_stage = fields.Date(string="Date Confirm Stage", required=False, )
    due_days = fields.Integer(string="Due Days", required=False, related='stage_id.due_days')
    num_days = fields.Date(string="Num Days", required=False, )

    ##############################33


    def send_notification_late(self):
        for rec in self:
            body = '<a target=_BLANK href="/web?#id=' + str(
                rec.id) + '&view_type=form&model=change.request.project&action=" style="font-weight: bold">' + str(
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
            stage_all = self.env['stage'].sudo().search([('workflow_id', '=', rec.workflow_id.id)], order='sequence')
            if not rec.stage_id:
                stage = self.env['stage'].sudo().search([('workflow_id', '=', rec.workflow_id.id)], limit=1,
                                                        order='sequence')
                print('stage', stage)
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
                stage = self.env['stage'].sudo().search(
                    [('sequence', '>', rec.stage_id.sequence), ('id', 'in', stage_all.ids)], limit=1, order='sequence')
                if stage:
                    if self.env.user.id not in stage.group_ids.users.ids:
                        raise UserError('You Cannot Confirm.')
                    else:
                        rec.stage_id = stage.id
                        rec.date_confirm_stage = fields.Date.today()
                        rec.num_days = rec.date_confirm_stage + timedelta(days=rec.due_days)
                else:
                    rec.is_hide_confirm = True
                    lines = []
                    for line in rec.contract_project_ids:
                        if line.contract_project_line_id:
                            rec.change_sub_line_revised(line)
                        else:
                            lines.append([0, 0, {
                                'company_id': line.company_id.id,
                                'currency_id': line.currency_id.id,
                                'item_id': line.item_id.id,
                                'name': line.name,
                                'work_type': line.work_type,
                                'work_package_id': line.work_package_id.id,
                                'quantity': line.quantity,
                                'unit_price': line.unit_price,
                                'uom_id': line.uom_id.id,
                                'tax_ids': line.tax_ids.ids,
                                # 'project_sub_line_ids': sub_line,
                                'display_type': line.display_type,
                            }])
                    rec.contract_project_id.contract_project_ids = lines
                    rec.state = 'confirm'

    @api.depends('contract_project_ids')
    def get_total_untaxed_amount(self):
        for rec in self:
            rec.total_untaxed_amount = sum(rec.contract_project_ids.mapped('untaxed_amount'))


    @api.constrains('contract_project_ids')
    def get_sub_date(self):
        for rec in self:
            if not rec.is_get_data:
                for line in rec.contract_project_ids:
                    line.project_sub_line_ids = [[0, 0, {
                        'contract_project_sub_line_id': sub.id,
                        'company_id': sub.company_id.id,
                        'currency_id': sub.currency_id.id,
                        'item_id': sub.item_id.id,
                        'name': sub.name,
                        'work_type': sub.work_type,
                        'work_package_id': sub.work_package_id.id,
                        'quantity': sub.quantity,
                        'unit_price': sub.unit_price,
                        'uom_id': sub.uom_id.id,
                        'tax_ids': sub.tax_ids.ids,
                        'untaxed_amount': sub.untaxed_amount,
                        'amount_tax': sub.amount_tax,
                        'total_amount': sub.total_amount,
                        'display_type': sub.display_type,

                    }] for sub in line.contract_project_line_id.project_sub_line_ids]
                rec.is_get_data =True

    def change_sub_line_revised(self,line):
        sub_line=[]
        for sub in line.project_sub_line_ids:
            if sub.contract_project_sub_line_id:
                sub.contract_project_sub_line_id.revised_quantity += sub.quantity
                sub.contract_project_sub_line_id.revised_unit_price += sub.unit_price
                sub.contract_project_sub_line_id.revised_untaxed_amount += sub.untaxed_amount
            else:
                sub_line.append([0, 0, {
                        'company_id': sub.company_id.id,
                        'currency_id': sub.currency_id.id,
                        'item_id': sub.item_id.id,
                        'name': sub.name,
                        'work_type': sub.work_type,
                        'work_package_id': sub.work_package_id.id,
                        'revised_quantity': sub.quantity,
                        'revised_unit_price': sub.unit_price,
                        'uom_id': sub.uom_id.id,
                        'tax_ids': sub.tax_ids.ids,
                        'revised_untaxed_amount': sub.untaxed_amount,
                        'display_type': sub.display_type,

                    }])
        line.contract_project_line_id.project_sub_line_ids = sub_line

    # def action_confirm(self):
    #     for rec in self:
    #         lines = []
    #         for line in rec.contract_project_ids:
    #             if line.contract_project_line_id:
    #                 rec.change_sub_line_revised(line)
    #             else:
    #                 lines.append([0, 0, {
    #                     'company_id': line.company_id.id,
    #                     'currency_id': line.currency_id.id,
    #                     'item_id': line.item_id.id,
    #                     'name': line.name,
    #                     'work_type': line.work_type,
    #                     'work_package_id': line.work_package_id.id,
    #                     'quantity': line.quantity,
    #                     'unit_price': line.unit_price,
    #                     'uom_id': line.uom_id.id,
    #                     'tax_ids': line.tax_ids.ids,
    #                     # 'project_sub_line_ids': sub_line,
    #                     'display_type': line.display_type,
    #                 }])
    #         rec.contract_project_id.contract_project_ids = lines
    #         rec.state = 'confirm'
