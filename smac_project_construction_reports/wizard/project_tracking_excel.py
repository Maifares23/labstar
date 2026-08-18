from odoo import models


class ProjectTrackingXlsx(models.AbstractModel):
    _name = "report.smac_project_construction_reports.tracking_excel"
    _inherit = "report.report_xlsx.abstract"
    _description = "Project Tracking XLSX"

    @staticmethod
    def _date_value(value):
        return str(value) if value else ""

    def generate_xlsx_report(self, workbook, data, objs):
        project_ids = (data or {}).get("projects_ids", [])
        projects = self.env["construction.project"].browse(project_ids).exists()
        sheet = workbook.add_worksheet("Project Tracking")

        main_title = workbook.add_format({
            "font_size": 16,
            "border": True,
            "align": "center",
            "valign": "vcenter",
            "bold": True,
            "bg_color": "#008080",
            "font_color": "white",
        })
        space_title = workbook.add_format({
            "align": "center",
            "valign": "vcenter",
            "bg_color": "white",
            "font_color": "white",
        })
        header_format = workbook.add_format({
            "font_size": 14,
            "border": True,
            "valign": "vcenter",
            "align": "center",
            "bg_color": "#008080",
            "font_color": "white",
            "bold": True,
            "text_wrap": True,
        })
        line_format = workbook.add_format({
            "font_size": 12,
            "border": True,
            "valign": "vcenter",
            "align": "center",
        })

        end_col = 21
        for blank_row in range(4):
            sheet.merge_range(blank_row, 0, blank_row, end_col, "", space_title)
        row = 4

        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 2, 35)
        sheet.set_column(3, end_col, 22)
        sheet.set_row(row, 25)
        sheet.merge_range(row, 1, row, 6, "Project Tracking", main_title)
        sheet.merge_range(row, 7, row, end_col, "", space_title)
        row += 3

        headers = [
            "Count",
            "Subcontractor",
            "Contract",
            "Invoice",
            "Revision",
            "Period From",
            "Period To",
            "Invoice Status",
            "Request Date",
            "Issue Date",
            "Approval Date",
            "Actual Approval Period",
            "Revised Contract",
            "Current Gross Amount",
            "Current Net Amount",
            "Invoice Amount + VAT",
            "Payment Due Date",
            "Over Due (Days)",
            "Priority Date (By PM)",
            "Paid Amount",
            "Payment Date",
            "Payment Status",
        ]
        sheet.set_row(row, 50)
        for col, title in enumerate(headers):
            sheet.write(row, col, title, header_format)
        row += 1

        counter = 0
        Contract = self.env["contract.project"].sudo()
        Invoice = self.env["contract.invoice"].sudo()
        for project in projects:
            contracts = Contract.search([("project_id", "=", project.id)])
            for contract in contracts:
                invoices = Invoice.search([("contract_project_id", "=", contract.id)])
                for invoice in invoices:
                    counter += 1
                    subcontractor = getattr(contract, "subcontractor_id", False)
                    code = getattr(contract, "code", False)
                    contract_name = contract.name or ""
                    contract_label = f"{contract_name} {code}".strip() if code else contract_name
                    stage = getattr(invoice, "stage_id", False)
                    workflow = getattr(invoice, "workflow_id", False)
                    workflow_stages = getattr(workflow, "stage_ids", self.env["ir.model"]) if workflow else False
                    first_stage = workflow_stages[:1] if workflow_stages else False
                    contract_lines = getattr(contract, "contract_project_ids", self.env["contract.project"])

                    values = [
                        counter,
                        subcontractor.display_name if subcontractor else "",
                        contract_label,
                        invoice.name or "",
                        "",
                        self._date_value(getattr(invoice, "date_from", False)),
                        self._date_value(getattr(invoice, "date_to", False)),
                        stage.display_name if stage else "",
                        self._date_value(getattr(contract, "contract_date", False)),
                        "",
                        "",
                        getattr(first_stage, "due_days", 0) if first_stage else "",
                        sum(contract_lines.mapped("revised_untaxed_amount")) if contract_lines else 0.0,
                        getattr(invoice, "accumulative_gross_amount_to_date", 0.0) or 0.0,
                        getattr(invoice, "cumulative_net_amount", 0.0) or 0.0,
                    ] + [""] * 7
                    for col, value in enumerate(values):
                        sheet.write(row, col, value, line_format)
                    row += 1
