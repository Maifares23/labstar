from odoo import fields, models


class ProjectDeductionsReport(models.TransientModel):
    _name = "project.deductions.wizard"
    _description = "Project Deductions Report"

    projects_ids = fields.Many2many(
        comodel_name="construction.project",
        string="Projects",
        required=True,
    )

    def action_project_deductions_excel(self):
        self.ensure_one()
        return self.env.ref(
            "smac_project_construction_reports.deductions_excel_action"
        ).report_action(self, data={"projects_ids": self.projects_ids.ids})
