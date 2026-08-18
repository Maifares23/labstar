# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
from datetime import timedelta


class ContractProjectSubLine(models.Model):
    _name = 'contract.invoice.sub.line'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Contract Project SubLine'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    wbs_id = fields.Many2one(comodel_name="wbs", string="Wbs", required=False, )
    name = fields.Char(string='Description', tracking=True)

    quantity = fields.Float(string="Quantity", required=False, )
    uom_id = fields.Many2one(comodel_name="uom.uom", string="Uom", required=False, )
    progress = fields.Float(string="progress %", required=False, )
    quantity_after_progres = fields.Float(string="Quantity After Progres", required=False,
                                          compute='get_quantity_after_progres')
    remarks = fields.Text(string="Remarks", required=False, )
    contract_invoice_line_id = fields.Many2one(comodel_name="contract.invoice.line", string="Contract Line",
                                               required=False, )
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    @api.depends('quantity', 'progress')
    def get_quantity_after_progres(self):
        for rec in self:
            rec.quantity_after_progres = rec.quantity * rec.progress / 100

    # @api.onchange('item_id')
    # def get_name_item(self):
    #     for rec in self:
    #         rec.name = rec.item_id.name
    #
    # @api.depends('tax_ids', 'quantity', 'unit_price')
    # def get_total_before_discount(self):
    #     for rec in self:
    #         untaxed_amount = rec.quantity * rec.unit_price
    #         taxes = rec.tax_ids.compute_all(untaxed_amount, self.env.user.company_id.currency_id, 1)
    #         rec.untaxed_amount = taxes['total_excluded']
    #         rec.amount_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
    #         rec.total_amount = taxes['total_included']


class ContractProjectLine(models.Model):
    _name = 'contract.invoice.line'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Contract Project Line'

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
    quantity = fields.Float(string="Revised  Quantity", required=False, default=1)
    uom_id = fields.Many2one(comodel_name="uom.uom", string="Uom", required=False, )
    unit_price = fields.Float(string="Unit Price", store=True, tracking=True, readonly=False)
    tax_ids = fields.Many2many('account.tax', string="Taxes", tracking=True)
    untaxed_amount = fields.Float(string="Revised Amount", compute="get_total_before_discount", tracking=True)
    amount_tax = fields.Float(string="Amount Tax", compute="get_total_before_discount", store=True, tracking=True)
    total_amount = fields.Float(string="Total Amount", compute="get_total_before_discount", store=True, tracking=True)
    contract_invoice_id = fields.Many2one(comodel_name="contract.invoice", string="Contract Project", required=False, )

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    previous_progress = fields.Float(string="Previous Progress %", required=False, )
    previous_qty = fields.Float(string="Previous Qty", required=False, )
    previous_amount = fields.Float(string="Previous Amount", required=False, )
    current_progress = fields.Float(string="Current Progress %", required=False,
                                    compute='get_quantity_progress_current_to_date')
    current_qty = fields.Float(string="Current Qty", required=False, compute='get_quantity_progress_current_to_date')
    current_amount = fields.Float(string="Current Amount", required=False,
                                  compute='get_quantity_progress_current_to_date')
    to_date_progress = fields.Float(string="To Date Progress %", required=False,
                                    compute='get_quantity_progress_current_to_date')
    to_date_qty = fields.Float(string="To Date Qty", required=False, compute='get_quantity_progress_current_to_date')
    to_date_amount = fields.Float(string="To Date Amount", required=False,
                                  compute='get_quantity_progress_current_to_date')
    contract_invoice_sub_line_ids = fields.One2many(comodel_name="contract.invoice.sub.line",
                                                    inverse_name="contract_invoice_line_id", string="",
                                                    required=False, )
    count_confirm = fields.Integer(string="Count Confirm", related='contract_invoice_id.count_confirm')
    contract_project_sub_line_id = fields.Many2one(comodel_name="contract.project.sub.line", string="",
                                                   required=False, )

    @api.constrains('contract_invoice_sub_line_ids', 'contract_invoice_sub_line_ids.quantity_after_progres')
    def validation_revised_quantity(self):
        for rec in self:
            total_quantity = sum(rec.contract_invoice_sub_line_ids.mapped('quantity_after_progres'))
            if total_quantity > rec.quantity:
                raise UserError('total quantity > revised quantity.')

    @api.depends('contract_invoice_sub_line_ids', 'contract_invoice_sub_line_ids.quantity_after_progres', 'to_date_qty')
    def get_quantity_progress_current_to_date(self):
        for rec in self:
            rec.to_date_qty = sum(rec.contract_invoice_sub_line_ids.mapped('quantity_after_progres'))
            rec.to_date_progress = rec.to_date_qty / rec.quantity * 100 if rec.quantity > 0 else 0
            rec.to_date_amount = rec.to_date_qty * rec.unit_price
            rec.current_progress = rec.to_date_progress - rec.previous_progress
            rec.current_qty = rec.to_date_qty - rec.previous_qty
            rec.current_amount = rec.to_date_amount - rec.previous_amount

    def view_transaction_line_pop_up(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Transaction Lines',
            'res_model': 'contract.invoice.line',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    # @api.onchange('item_id')
    # def get_name_item(self):
    #     for rec in self:
    #         rec.name = rec.item_id.name

    @api.depends('tax_ids', 'quantity', 'unit_price')
    def get_total_before_discount(self):
        for rec in self:
            untaxed_amount = rec.quantity * rec.unit_price
            taxes = rec.tax_ids.compute_all(untaxed_amount, self.env.user.company_id.currency_id, 1)
            rec.untaxed_amount = taxes['total_excluded']
            rec.amount_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            rec.total_amount = taxes['total_included']


class ContractInvoice(models.Model):
    _name = 'contract.invoice'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Contract Invoice'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    contract_project_id = fields.Many2one(comodel_name="contract.project", string="Contract", required=False,
                                          tracking=True, )
    name = fields.Char(string='Name', tracking=True, readonly=True, default='New', )
    project_id = fields.Many2one(comodel_name="construction.project", string="Project", required=False, tracking=True)
    code = fields.Char(string='Code', tracking=True, related='contract_project_id.code')
    subcontractor_id = fields.Many2one(comodel_name="res.partner", string="Subcontractor", required=False,
                                       tracking=True)
    date_from = fields.Date(string="Date From", required=False, tracking=True, )
    date_to = fields.Date(string="Date To", required=False, tracking=True, )
    check_final_invoice = fields.Boolean(
        string='Final invoice',
        required=False)

    state = fields.Selection(string="State", selection=[('draft', 'Draft'), ('confirm', 'Confirm'), ], required=False,
                             default='draft', tracking=True, )

    # contract_information
    original_contract_amount = fields.Float(string="Original Contract Amount", required=False, compute='get_summary')
    advanced_payment_percentage = fields.Float(string="Advanced Payment %", required=False, compute='get_summary')
    contract_advanced_payment = fields.Float(string="Contract Advanced Payment", required=False, compute='get_summary')
    change_orders_amount = fields.Float(string="Change Orders Amount", required=False, compute='get_summary')
    total_contract_amount_after_change_order = fields.Float(string="Total Contract Amount After Change Order",
                                                            required=False, compute='get_summary')

    # progress_information
    accumulative_gross_amount_to_date = fields.Float(string="Accumulative Gross Amount To Date", required=False,
                                                     compute='get_summary')
    # liabilities
    total_backlog_deduction_amount = fields.Float(string="Total Backlog Deduction Amount", required=False,
                                                  compute='get_deductions')
    prepaid_advanced_payment = fields.Float(string="Prepaid Advanced Payment", required=False, )
    # deduction
    cumulative_advanced_payment = fields.Float(string="Cumulative Advanced Payment", required=False, )
    site_deductions = fields.Float(string="Site Deductions", required=False, compute='get_deductions')
    total_deductions = fields.Float(string="Total Deductions", required=False, compute='get_summary')
    # invoice_amount
    cumulative_net_amount = fields.Float(string="Cumulative Net Amount", required=False, compute='get_summary')
    previous_net_amount = fields.Float(string="Previous Net Amount", required=False, )
    current_net_amount = fields.Float(string="Current Net Amount", required=False, )
    cumulative_retention = fields.Float(string="Cumulative Retention", required=False, compute='get_summary')
    contract_advanced_payment_adjustment = fields.Float(string="Contract Advanced Payment Adjustment", required=False, )
    previous_outstanding_payment = fields.Float(string="Previous Outstanding Payment", required=False, )
    outstanding_payment_for_this_period = fields.Float(string="Previous Outstanding Payment For This Period",
                                                       required=False, compute='get_summary')
    ###############
    contract_invoice_ids = fields.One2many(comodel_name="contract.invoice.line", inverse_name="contract_invoice_id",
                                           string="", required=False, )
    count_confirm = fields.Integer(string="Count Confirm", required=False, copy=False)
    #########################################
    deduction_ids = fields.Many2many(comodel_name="deductions", string="Deductions",
                                     domain="[('is_hide_confirm', '=', True),('is_confirm_invoice', '!=', True)]")

    # workflow
    stage_id = fields.Many2one(comodel_name="stage", string="Stage", required=False,
                               domain="[('workflow_id', '=', workflow_id)]")
    workflow_id = fields.Many2one(comodel_name="workflow", string="Workflow", required=False)
    is_hide_confirm = fields.Boolean(string="Hide Confirm", )
    date_confirm_stage = fields.Date(string="Date Confirm Stage", required=False, )
    due_days = fields.Integer(string="Due Days", required=False, related='stage_id.due_days')
    num_days = fields.Date(string="Num Days", required=False, )

    ##############################33
    def send_notification_late(self):
        for rec in self:
            body = '<a target=_BLANK href="/web?#id=' + str(
                rec.id) + '&view_type=form&model=contract.invoice&action=" style="font-weight: bold">' + str(
                rec.name) + '</a>'

            partners = [x.partner_id.id for x in rec.stage_id.mapped('group_ids').mapped('users')]
            partners_mangers = [x.partner_id.id for x in
                                rec.stage_id.mapped('group_ids').mapped('users').mapped('managers_ids')]
            partners.extend(partners_mangers)
            print('partners', partners)
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


    @api.onchange('workflow_id')
    def get_stage_id(self):
        for rec in self:
            rec.stage_id = False

    def action_confirm(self):
        for rec in self:
            if rec.check_final_invoice and rec.total_backlog_deduction_amount != 0:
                raise ValidationError(_("Total Backlog Not Equal Zero"))
            stage_all = self.env['stage'].sudo().search([('workflow_id', '=', rec.workflow_id.id)],
                                                        order='sequence')
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
                    [('sequence', '>', rec.stage_id.sequence), ('id', 'in', stage_all.ids)], limit=1,
                    order='sequence')
                if stage:
                    if self.env.user.id not in stage.group_ids.users.ids:
                        raise UserError('You Cannot Confirm.')
                    else:
                        rec.stage_id = stage.id
                        rec.date_confirm_stage = fields.Date.today()
                        rec.num_days = rec.date_confirm_stage + timedelta(days=rec.due_days)
                else:
                    rec.is_hide_confirm = True
                    rec.deduction_ids.sudo().write({'is_confirm_invoice': True})
                    last_invoice_confirm = self.sudo().search(
                        [('contract_project_id', '=', rec.contract_project_id.id), ('state', '=', 'confirm'),
                         ('id', '!=', rec.id)]).mapped('count_confirm')
                    print('last_invoice_confirm', last_invoice_confirm)
                    if last_invoice_confirm:
                        rec.count_confirm = max(last_invoice_confirm) + 1
                    else:
                        rec.count_confirm = 1

    @api.depends('contract_project_id', 'deduction_ids')
    def get_deductions(self):
        for rec in self:
            deduction_select_amount = sum(
                self.sudo().search([('deduction_ids', '!=', False)]).mapped('deduction_ids').mapped('total_amount'))
            print('deduction_select_amount', deduction_select_amount)
            all_deductions = sum(self.env['deductions'].sudo().search(
                [('is_hide_confirm', '=', True), ('is_confirm_invoice', '!=', True)]).mapped('total_amount'))
            rec.total_backlog_deduction_amount = all_deductions - deduction_select_amount
            rec.site_deductions = sum(rec.deduction_ids.mapped('total_amount'))

    @api.depends('contract_project_id')
    def get_summary(self):
        for rec in self:
            accumulative_gross_amount_to_date = sum(rec.contract_invoice_ids.mapped('current_amount'))
            ###########3
            rec.original_contract_amount = rec.contract_project_id.total_untaxed_amount
            rec.advanced_payment_percentage = rec.contract_project_id.advanced_payment_percentage
            rec.contract_advanced_payment = rec.contract_project_id.advanced_payment_amount
            # rec.change_orders_amount = rec.contract_project_id.change_orders_amount
            rec.change_orders_amount = rec.contract_project_id.total_revised_untaxed_amount - rec.original_contract_amount
            rec.total_contract_amount_after_change_order = rec.contract_project_id.total_revised_untaxed_amount
            rec.accumulative_gross_amount_to_date = accumulative_gross_amount_to_date
            rec.cumulative_advanced_payment = rec.advanced_payment_percentage * accumulative_gross_amount_to_date / 100
            rec.total_deductions = rec.cumulative_advanced_payment + rec.site_deductions
            rec.cumulative_net_amount = rec.accumulative_gross_amount_to_date - rec.total_deductions
            rec.cumulative_retention = rec.contract_project_id.retention_payment_percentage * rec.accumulative_gross_amount_to_date / 100
            rec.outstanding_payment_for_this_period = rec.cumulative_net_amount - rec.cumulative_retention

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                code = vals.get('code')
                if not code and vals.get('contract_project_id'):
                    code = self.env['contract.project'].browse(vals['contract_project_id']).code
                sequence = self.env['ir.sequence'].next_by_code('contract.invoice.Sequence') or _('New')
                vals['name'] = 'Inv / %s%s' % (code or '', sequence)
        return super().create(vals_list)

    # def action_confirm(self):
    #     for rec in self:
    #         rec.state = 'confirm'
    #         last_invoice_confirm = self.sudo().search([('contract_project_id','=',rec.contract_project_id.id),('state','=','confirm'),('id','!=',rec.id)]).mapped('count_confirm')
    #         print('last_invoice_confirm',last_invoice_confirm)
    #         if last_invoice_confirm:
    #             rec.count_confirm = max(last_invoice_confirm) + 1
    #         else:
    #             rec.count_confirm = 1
