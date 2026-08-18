# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta



class ContractProjectSubLine(models.Model):
    _name = 'contract.project.sub.line'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Contract Project SubLine'

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
    contract_line_id = fields.Many2one(comodel_name="contract.project.line", string="Contract Line", required=False, )
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    revised_quantity = fields.Float(string="Revised Quantity", required=False, )
    revised_unit_price = fields.Float(string="Revised Unit Price",
                                      store=True, tracking=True, readonly=False)
    revised_untaxed_amount = fields.Float(string="Revised Untaxed Amount",
                                          tracking=True)
    revised_amount_tax = fields.Float(string="Revised Amount Tax",
                                      store=True, tracking=True)

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


class ContractProjectLine(models.Model):
    _name = 'contract.project.line'
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
    contract_project_id = fields.Many2one(comodel_name="contract.project", string="Contract Project", required=False, )
    project_sub_line_ids = fields.One2many(comodel_name="contract.project.sub.line", inverse_name="contract_line_id",
                                           string="", required=False, )
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    revised_quantity = fields.Float(string="Revised Quantity", required=False, compute="get_total_before_discount")
    revised_unit_price = fields.Float(string="Revised Unit Price",
                                      store=True, tracking=True, readonly=False, compute="get_total_before_discount")
    revised_untaxed_amount = fields.Float(string="Revised Untaxed Amount", compute="get_total_before_discount",
                                          tracking=True)
    revised_amount_tax = fields.Float(string="Revised Amount Tax", store=True, tracking=True, )

    def view_sub_line_pop_up(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Items Lines',
                'res_model': 'contract.project.line',
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
            rec.unit_price = sum(
                rec.project_sub_line_ids.mapped('unit_price')) / sum(
                rec.project_sub_line_ids.mapped('quantity')) if sum(rec.project_sub_line_ids.mapped('quantity')) > 0  else rec.unit_price
            rec.revised_quantity = sum(rec.project_sub_line_ids.mapped('revised_quantity')) if sum(
                rec.project_sub_line_ids.mapped('revised_quantity')) > 0 else rec.quantity
            rec.revised_unit_price = sum(rec.project_sub_line_ids.mapped('revised_unit_price')) if sum(
                rec.project_sub_line_ids.mapped('revised_unit_price')) > 0 else rec.unit_price
            taxes = rec.tax_ids.compute_all(untaxed_amount, self.env.user.company_id.currency_id, 1)
            rec.untaxed_amount = taxes['total_excluded']
            rec.revised_untaxed_amount = sum(rec.project_sub_line_ids.mapped('revised_untaxed_amount')) if sum(
                rec.project_sub_line_ids.mapped('revised_untaxed_amount')) > 0 else rec.untaxed_amount
            # taxes = rec.tax_ids.compute_all(untaxed_amount, self.env.user.company_id.currency_id, 1)
            # rec.untaxed_amount = taxes['total_excluded']
            rec.amount_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            rec.total_amount = taxes['total_included']


class ContractProject(models.Model):
    _name = 'contract.project'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Contract Project'

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
    contract_project_ids = fields.One2many(comodel_name="contract.project.line", inverse_name="contract_project_id",
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
    advanced_payment_percentage = fields.Float(string="Advanced Payment(%)", required=False, readonly=False,
                                               tracking=True)
    advanced_payment_amount = fields.Float(required=False, readonly=False, tracking=True,
                                           compute='get_advanced_payment_percentage')

    retention_payment_percentage = fields.Float(string="Retention (%)", required=False, readonly=False, tracking=True)
    retention_payment_amount = fields.Float(required=False, readonly=False, tracking=True,
                                            compute='get_retention_payment_percentage')

    state = fields.Selection(string="State", selection=[('draft', 'Draft'), ('confirm', 'Confirm'), ], required=False,
                             default='draft')
    total_untaxed_amount = fields.Float(string="Total Untaxed Amount", required=False, readonly=False, tracking=True,
                                        compute='get_total_amount')
    total_revised_untaxed_amount = fields.Float(string="Total Revised Untaxed Amount", required=False, readonly=False,
                                                tracking=True, compute='get_total_amount')
    change_orders_amount = fields.Float(string="Change Orders Amount", required=False, readonly=False, tracking=True,
                                        compute='get_change_orders_amount')

    # workflow
    stage_id = fields.Many2one(comodel_name="stage", string="Stage", required=False,
                               domain="[('workflow_id', '=', workflow_id)]")
    workflow_id = fields.Many2one(comodel_name="workflow", string="Contract Workflow", required=True)
    deduction_workflow_id = fields.Many2one(comodel_name="workflow", string="Deduction Workflow", required=True)
    invoice_workflow_id = fields.Many2one(comodel_name="workflow", string="Invoice Workflow", required=True)
    change_request_workflow_id = fields.Many2one(comodel_name="workflow", string="Change Request Workflow", required=True)
    is_hide_confirm = fields.Boolean(string="Hide Confirm", )
    date_confirm_stage = fields.Date(string="Date Confirm Stage", required=False, )
    due_days = fields.Integer(string="Due Days", required=False,related='stage_id.due_days' )
    num_days = fields.Date(string="Num Days", required=False,)
    # compute='get_num_days' )

    # @api.depends('date_confirm_stage','due_days')
    # def get_num_days(self):
    #     for rec in self:
    #         rec.num_days = rec.date_confirm_stage + timedelta(days=rec.due_days)
    ##############################33
    def compute_check_stage_action(self):
        stage_policy = self.env['ir.config_parameter'].sudo().get_param('stage_policy',)
        print('stage_policy',stage_policy)
        contracts = self.search([('num_days', '=', fields.Date.today())])
        contract_invoices = self.env['contract.invoice'].search([('num_days', '=', fields.Date.today())])
        change_requests = self.env['change.request.project'].sudo().search([('num_days', '=', fields.Date.today())])
        print('fields.Date.today()',fields.Date.today())
        print('change_requests',change_requests)
        deductions = self.env['deductions'].search([('num_days', '=', fields.Date.today())])
        if stage_policy == 'next_stage':
            for contract in contracts:
                if not contract.is_hide_confirm:
                    contract.action_confirm()
            for invoice in contract_invoices:
                if not invoice.is_hide_confirm:
                    invoice.action_confirm()
            for change_request in change_requests:
                if not change_request.is_hide_confirm:
                    change_request.action_confirm()
            for deduction in deductions:
                if not deduction.is_hide_confirm:
                    deduction.action_confirm()
        elif stage_policy == 'send_mail':
            for contract in contracts:
                if not contract.is_hide_confirm:
                    print('yyyyyyyyyyyyyyyy')
                    contract.send_notification_late()
            for invoice in contract_invoices:
                if not invoice.is_hide_confirm:
                    invoice.send_notification_late()
            for change_request in change_requests:
                print('change_request',change_request)
                if not change_request.is_hide_confirm:
                    change_request.send_notification_late()
            for deduction in deductions:
                if not deduction.is_hide_confirm:
                    deduction.send_notification_late()


    ##################################3
    # def send_notification_late(self):
    #     for rec in self:
    #         body = '<a target=_BLANK href="/web?#id=' + str(
    #             rec.id) + '&view_type=form&model=contract.project&action=" style="font-weight: bold">' + str(
    #             rec.name) + '</a>'
    #
    #         partners = [x.partner_id.id for x in rec.stage_id.mapped('group_ids').mapped('users')]
    #         partners_mangers = [x.partner_id.id for x in rec.stage_id.mapped('group_ids').mapped('users').mapped('managers_ids')]
    #         partners.extend(partners_mangers)
    #         print('partners',partners)
    #         partners = list(set(partners))
    #         print('partners', partners)
    #         # partners = [rec.project_id.user_id.partner_id.id]
    #         if partners:
    #             thread_pool = self.env['mail.thread']
    #             thread_pool.sudo().message_notify(
    #                 partner_ids=partners,
    #                 subject="Form " + str(rec.name) + " You Should Approve This Transaction",
    #                 body="Message:Form  " + str(body) + " You Should Approve This Transaction",
    #                 email_from=self.env.user.company_id.email)
    #
    # def send_notification(self,line):
    #     for rec in self:
    #         body = '<a target=_BLANK href="/web?#id=' + str(
    #             rec.id) + '&view_type=form&model=contract.project&action=" style="font-weight: bold">' + str(
    #             rec.name) + '</a>'
    #         if line:
    #             partners = set([x.partner_id.id for x in line.stage_ids.mapped('group_ids').mapped('users')])
    #             print('partners',partners)
    #
    #             print('partners', partners)
    #             # partners = [rec.project_id.user_id.partner_id.id]
    #             if partners:
    #                 thread_pool = self.env['mail.thread']
    #                 thread_pool.sudo().message_notify(
    #                     partner_ids=partners,
    #                     subject="Form " + str(rec.name) + " You Will Approve Transaction For This Contract",
    #                     body="Message:Form  " + str(body) + " You Will Approve Transaction For This Contract",
    #                     email_from=self.env.user.company_id.email)


    ###########################333

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
                    # rec.send_notification(rec.deduction_workflow_id)
                    # rec.send_notification(rec.invoice_workflow_id)
                    # rec.send_notification(rec.change_request_workflow_id)

    @api.depends('contract_project_ids')
    def get_change_orders_amount(self):
        for rec in self:
            change_requests = self.env['change.request.project'].sudo().search([('contract_project_id', '=', rec.id)])
            rec.change_orders_amount = sum(change_requests.mapped('total_untaxed_amount'))

    @api.depends('contract_project_ids')
    def get_total_amount(self):
        for rec in self:
            rec.total_untaxed_amount = sum(rec.contract_project_ids.mapped('untaxed_amount'))
            rec.total_revised_untaxed_amount = sum(rec.contract_project_ids.mapped('revised_untaxed_amount'))

    @api.depends('advanced_payment_percentage', 'total_revised_untaxed_amount')
    def get_advanced_payment_percentage(self):
        for rec in self:
            rec.advanced_payment_amount = (
                rec.total_revised_untaxed_amount * rec.advanced_payment_percentage / 100
            )

    @api.depends('retention_payment_percentage', 'total_revised_untaxed_amount')
    def get_retention_payment_percentage(self):
        for rec in self:
            rec.retention_payment_amount = (
                rec.total_revised_untaxed_amount * rec.retention_payment_percentage / 100
            )

    # def action_confirm(self):
    #     for rec in self:
    #         stage_all = self.env['stage'].sudo().search([('workflow_id', '=', rec.workflow_id.id)], order='sequence')
    #         if not rec.stage_id:
    #             stage = self.env['stage'].sudo().search([('workflow_id', '=', rec.workflow_id.id)], limit=1,
    #                                                     order='sequence')
    #             print('stage', stage)
    #             if self.env.user.id not in stage.group_ids.users.ids:
    #                 raise UserError('You Cannot Confirm.')
    #             else:
    #                 rec.stage_id = stage.id
    #                 ########################
    #         else:
    #             stage = self.env['stage'].sudo().search(
    #                 [('sequence', '>', rec.stage_id.sequence), ('id', 'in', stage_all.ids)], limit=1, order='sequence')
    #             if stage:
    #                 if self.env.user.id not in stage.group_ids.users.ids:
    #                     raise UserError('You Cannot Confirm.')
    #                 else:
    #                     rec.stage_id = stage.id
    #             else:
    #                 rec.is_hide_confirm = True

    def get_change_request_sub_line(self, line):
        sub_lines = [[0, 0, {
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

        }] for sub in line.project_sub_line_ids]
        print('sub_lines', sub_lines)
        return sub_lines

    def get_change_request_line(self):
        for rec in self:
            lines = []
            for line in rec.contract_project_ids:
                sub_line = rec.get_change_request_sub_line(line)
                lines.append([0, 0, {
                    'contract_project_line_id': line.id,
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
                    'untaxed_amount': line.untaxed_amount,
                    'amount_tax': line.amount_tax,
                    'total_amount': line.total_amount,
                    'project_sub_line_ids': sub_line,
                    'display_type': line.display_type,
                }])
        print('lines', lines)
        return lines

    def get_change_request(self):
        lines = self.get_change_request_line()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Change Request',
            'res_model': 'change.request.project',
            'view_mode': 'list,form',
            'context': {
                'default_contract_project_id': self.id,
                'default_project_id': self.project_id.id,
                'default_workflow_id': self.change_request_workflow_id.id,
                'default_company_id': self.company_id.id,
                'default_currency_id': self.currency_id.id,
                'default_subcontractor_id': self.subcontractor_id.id,
                'default_date_from': self.date_from,
                'default_date_to': self.date_to,
                'default_work_type': self.work_type,
                'default_disciplines_id': self.disciplines_id.id,
                'default_description_custom': self.description_custom,
                'default_open_end_contract': self.open_end_contract,
                'default_open_cost_contract': self.open_cost_contract,
                'default_contract_duration': self.contract_duration,
                'default_contract_payment_duration': self.contract_payment_duration,
                'default_contract_date': self.contract_date,
                'default_contract_project_ids': lines,

            },
            'domain': [('contract_project_id', '=', self.id)],
        }

    ####################################invoice
    def get_invoice_sub_line(self, line):
        sub_lines = [[0, 0, {
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

        }] for sub in line.project_sub_line_ids]
        print('sub_lines', sub_lines)
        return sub_lines

    def get_contract_invoice_ids(self):
        for rec in self:
            lines = []
            for line in rec.contract_project_ids:
                # sub_line = rec.get_invoice_sub_line(line)

                lines.append([0, 0, {
                    'name': line.name,
                    'display_type': 'line_section',
                }])
                for sub in line.project_sub_line_ids:
                    previous_progress = 0
                    previous_qty = 0
                    previous_amount = 0
                    contract_invoice_line_max = self.env['contract.invoice.line'].sudo().search(
                        [('contract_invoice_id.state', '=', 'confirm'),
                         ('contract_invoice_id.contract_project_id', '=', rec.id),
                         ('contract_project_sub_line_id', '=', sub.id)]).mapped('count_confirm')
                    # print('max_contract_invoice_line',max_contract_invoice_line)
                    if contract_invoice_line_max:
                        max_contract_invoice_line = max(contract_invoice_line_max)
                        # if max_contract_invoice_line:
                        contract_invoice_line = self.env['contract.invoice.line'].sudo().search(
                            [('count_confirm', '=', max_contract_invoice_line),
                             ('contract_invoice_id.state', '=', 'confirm'),
                             ('contract_invoice_id.contract_project_id', '=', rec.id),
                             ('contract_project_sub_line_id', '=', sub.id)])

                        print('contract_invoice_line', contract_invoice_line)
                        print('contract_invoice_line.current_qty', contract_invoice_line.current_qty)
                        previous_progress = contract_invoice_line.current_progress
                        previous_qty = contract_invoice_line.current_qty
                        previous_amount = contract_invoice_line.current_amount
                        print('previous_qty', previous_qty)
                    lines.append([0, 0, {
                        'contract_project_sub_line_id': sub.id,
                        'company_id': sub.company_id.id,
                        'currency_id': sub.currency_id.id,
                        'item_id': sub.item_id.id,
                        'name': sub.name,
                        'work_type': sub.work_type,
                        'work_package_id': sub.work_package_id.id,
                        'quantity': sub.revised_quantity,
                        'unit_price': sub.revised_unit_price,
                        'uom_id': sub.uom_id.id,
                        'tax_ids': sub.tax_ids.ids,
                        'untaxed_amount': sub.revised_untaxed_amount,
                        'amount_tax': sub.revised_amount_tax,
                        'total_amount': sub.total_amount,
                        'display_type': sub.display_type,
                        'previous_progress': previous_progress,
                        'previous_qty': previous_qty,
                        'previous_amount': previous_amount,
                    }])
                print('lines', lines)
        return lines

    def get_invoice(self):
        lines = self.get_contract_invoice_ids()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'contract.invoice',
            'view_mode': 'list,form',
            'context': {
                'default_contract_project_id': self.id,
                'default_project_id': self.project_id.id,
                'default_workflow_id': self.invoice_workflow_id.id,
                'default_company_id': self.company_id.id,
                'default_currency_id': self.currency_id.id,
                'default_subcontractor_id': self.subcontractor_id.id,
                'default_code': self.code,
                # 'default_date_from': self.date_from,
                # 'default_date_to': self.date_to,

                'default_contract_invoice_ids': lines,

            },
            'domain': [('contract_project_id', '=', self.id)],
        }

    def get_deduction(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Deductions',
            'res_model': 'deductions',
            'view_mode': 'list,form',
            'context': {
                'default_contract_project_id': self.id,
                'default_project_id': self.project_id.id,
                'default_workflow_id': self.deduction_workflow_id.id,
                'default_company_id': self.company_id.id,
                'default_currency_id': self.currency_id.id,
                'default_subcontractor_id': self.subcontractor_id.id,
            },
            'domain': [('contract_project_id', '=', self.id)],
        }
