from odoo import models


class ContractsStatementsXlsx(models.AbstractModel):
    _name = "report.smac_project_construction_reports.statements_excel"
    _inherit = "report.report_xlsx.abstract"
    _description = "Contracts Statements XLSX"

    @staticmethod
    def _name_or_blank(record):
        return record.display_name if record else ""

    def generate_xlsx_report(self, workbook, data, objs):
        project_ids = (data or {}).get("projects_ids", [])
        projects = self.env["construction.project"].browse(project_ids).exists()
        sheet = workbook.add_worksheet("Project Statements")

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

        end_col = 19
        for blank_row in range(4):
            sheet.merge_range(blank_row, 0, blank_row, end_col, "", space_title)
        row = 4

        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 1, 40)
        sheet.set_column(2, end_col, 24)
        sheet.set_row(row, 25)
        sheet.merge_range(row, 1, row, 6, "Project Contracts Statement", main_title)
        sheet.merge_range(row, 7, row, end_col, "", space_title)
        row += 3

        headers = [
            "Count",
            "Subcontractor",
            "Contract",
            "Discipline",
            "Original Contract Amount",
            "Revised Contract Amount",
            "Accumulative Gross Amount To Date",
            "Accumulative Gross Amount To Date %",
            "Cumulative Net Amount",
            "Cumulative Net Amount %",
            "Cumulative Invoice Outstanding Payment",
            "Cumulative Invoice Paid Amount",
            "Cumulative Advanced Payment",
            "Paid Advanced Payment",
            "Contract Advanced Payment Adjustment",
            "Account Payable",
            "Retention Amount",
            "Committed Cost",
            "Remaining Outflow",
            "Financial Statement",
        ]
        sheet.set_row(row, 60)
        for col, title in enumerate(headers):
            sheet.write(row, col, title, header_format)
        row += 1

        counter = 0
        Contract = self.env["contract.project"].sudo()
        for project in projects:
            contracts = Contract.search([("project_id", "=", project.id)])
            for contract in contracts:
                counter += 1
                subcontractor = getattr(contract, "subcontractor_id", False)
                code = getattr(contract, "code", False)
                contract_name = contract.name or ""
                contract_label = f"{contract_name} {code}".strip() if code else contract_name
                discipline = getattr(contract, "disciplines_id", False)
                contract_lines = getattr(contract, "contract_project_ids", self.env["contract.project"])

                values = [
                    counter,
                    self._name_or_blank(subcontractor),
                    contract_label,
                    self._name_or_blank(discipline),
                    sum(contract_lines.mapped("untaxed_amount")) if contract_lines else 0.0,
                    sum(contract_lines.mapped("revised_untaxed_amount")) if contract_lines else 0.0,
                ] + [""] * 14
                for col, value in enumerate(values):
                    sheet.write(row, col, value, line_format)
                sheet.set_row(row, 25)
                row += 1
