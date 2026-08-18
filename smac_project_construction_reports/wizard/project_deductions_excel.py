from odoo import models


class ProjectDeductionsXlsx(models.AbstractModel):
    _name = "report.smac_project_construction_reports.deductions_excel"
    _inherit = "report.report_xlsx.abstract"
    _description = "Project Deductions XLSX"

    def generate_xlsx_report(self, workbook, data, objs):
        project_ids = (data or {}).get("projects_ids", [])
        projects = self.env["construction.project"].browse(project_ids).exists()
        sheet = workbook.add_worksheet("Project Deductions")

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

        end_col = 11
        for blank_row in range(4):
            sheet.merge_range(blank_row, 0, blank_row, end_col, "", space_title)
        row = 4

        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 2, 35)
        sheet.set_column(3, end_col, 22)
        sheet.set_row(row, 25)
        sheet.merge_range(row, 1, row, 6, "Project Deductions", main_title)
        sheet.merge_range(row, 7, row, end_col, "", space_title)
        row += 3

        headers = [
            "Count",
            "Subcontractor",
            "Contract",
            "Status",
            "Work Package",
            "Description",
            "Type",
            "Work Type",
            "U.O.M",
            "Unit Price",
            "Qty",
            "Amount",
        ]
        sheet.set_row(row, 35)
        for col, title in enumerate(headers):
            sheet.write(row, col, title, header_format)
        row += 1

        work_type_labels = {
            "supply": "Supply",
            "apply": "Apply",
            "equ": "Equipment Rental",
            "eng": "Engineering Rental",
            "manpower": "ManPower Rental",
        }
        counter = 0
        Contract = self.env["contract.project"].sudo()
        Deduction = self.env["deductions"].sudo()
        for project in projects:
            contracts = Contract.search([("project_id", "=", project.id)])
            for contract in contracts:
                deductions = Deduction.search([("contract_project_id", "=", contract.id)])
                for deduction in deductions:
                    for line in deduction.deduction_ids:
                        counter += 1
                        subcontractor = getattr(contract, "subcontractor_id", False)
                        code = getattr(contract, "code", False)
                        contract_name = contract.name or ""
                        contract_label = f"{contract_name} {code}".strip() if code else contract_name
                        work_package = getattr(line, "work_package_id", False)
                        uom = getattr(line, "uom_id", False)
                        values = [
                            counter,
                            subcontractor.display_name if subcontractor else "",
                            contract_label,
                            getattr(deduction, "state", "") or "",
                            work_package.display_name if work_package else "",
                            line.name or "",
                            "",
                            work_type_labels.get(getattr(line, "work_type", False), ""),
                            uom.display_name if uom else "",
                            getattr(line, "unit_price", 0.0) or 0.0,
                            getattr(line, "quantity", 0.0) or 0.0,
                            getattr(line, "amount", 0.0) or 0.0,
                        ]
                        for col, value in enumerate(values):
                            sheet.write(row, col, value, line_format)
                        row += 1
