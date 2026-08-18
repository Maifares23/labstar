from odoo import fields, models


class ProjectTrackingReport(models.TransientModel):
    _name = "project.tracking.wizard"
    _description = "Project Tracking Report"

    projects_ids = fields.Many2many(
        comodel_name="construction.project",
        string="Projects",
        required=True,
    )

    def action_project_tracking_excel(self):
        self.ensure_one()
        return self.env.ref(
            "smac_project_construction_reports.tracking_excel_action"
        ).report_action(self, data={"projects_ids": self.projects_ids.ids})
