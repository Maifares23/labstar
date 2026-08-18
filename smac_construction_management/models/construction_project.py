# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ConstructionProject(models.Model):
    _name = 'construction.project'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Construction Project'

    name = fields.Char(string='Name', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    code = fields.Char(string='Code', tracking=True)
    business_unit_id = fields.Many2one('business.unit', string='Business Unit', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', tracking=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', tracking=True)

    count_contracts = fields.Integer(compute='get_count_contracts')

    def get_count_contracts(self):
        for record in self:
            record.count_contracts = self.env['contract.project'].sudo().search_count([
                ('project_id', '=', record.id),
            ])

    def _project_action(self, name, model):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'res_model': model,
            'view_mode': 'list,form',
            'context': {'default_project_id': self.id},
            'domain': [('project_id', '=', self.id)],
        }

    def get_business_Unit(self):
        return self._project_action('Business Unit', 'business.unit')

    def get_man_power_types(self):
        return self._project_action('Man Power Types', 'man.power.types')

    def get_equipments(self):
        return self._project_action('Equipments', 'equipments')

    def get_contract_project(self):
        return self._project_action('Contracts', 'contract.project')

    def get_wbs(self):
        return self._project_action('WBS', 'wbs')

    def get_work_package(self):
        return self._project_action('Work Package', 'work.package')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        project_plan_id = int(self.env['ir.config_parameter'].sudo().get_param('analytic.project_plan', 0) or 0)
        default_plan = self.env['account.analytic.plan'].browse(project_plan_id).exists()

        for record in records:
            analytic_plan = self.env['account.analytic.plan'].search(
                [('business_unit_id', '=', record.business_unit_id.id)],
                limit=1,
            ) if record.business_unit_id else default_plan

            if analytic_plan:
                analytic_account = self.env['account.analytic.account'].create({
                    'name': record.name or record.display_name,
                    'plan_id': analytic_plan.id,
                    'company_id': record.company_id.id,
                })
                record.analytic_account_id = analytic_account.id
        return records
