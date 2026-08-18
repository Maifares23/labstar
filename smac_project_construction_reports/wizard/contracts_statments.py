from odoo import fields, models


class ContractsStatementsReport(models.TransientModel):
    _name = "contracts.statements.wizard"
    _description = "Contracts Statements Report"

    projects_ids = fields.Many2many(
        comodel_name="construction.project",
        string="Projects",
        required=True,
    )

    def action_project_statements_excel(self):
        self.ensure_one()
        return self.env.ref(
            "smac_project_construction_reports.statements_excel_action"
        ).report_action(self, data={"projects_ids": self.projects_ids.ids})
