from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    visit_form_count = fields.Integer(
        string="Visit Forms",
        compute="_compute_visit_form_count",
    )

    @api.depends("partner_id")
    def _compute_visit_form_count(self):
        VisitForm = self.env["crm.visit.form"]

        for lead in self:
            if lead.partner_id:
                lead.visit_form_count = VisitForm.search_count([
                    ("customer_id", "=", lead.partner_id.id),
                ])
            else:
                lead.visit_form_count = 0

    def action_open_visit_forms(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Visit Forms",
            "res_model": "crm.visit.form",
            "view_mode": "list,form",
            "domain": [
                ("customer_id", "=", self.partner_id.id),
            ],
            "context": {
                "default_customer_id": self.partner_id.id,
            },
        }