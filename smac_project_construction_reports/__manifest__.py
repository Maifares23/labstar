# -*- coding: utf-8 -*-
{
    "name": "Project Construction Reports Excel",
    "summary": "Excel reports for construction projects and contracts",
    "description": """
XLSX reports for project contract statements, deductions, and tracking.
Compatible with Odoo 18 and the OCA report_xlsx framework.
    """,
    "author": "SMAC",
    "website": "https://www.yourcompany.com",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "depends": [
        "smac_construction_management",
        "report_xlsx",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/contracts_statements.xml",
        "wizard/project_deductions.xml",
        "wizard/project_tracking.xml",
        "reports/reports_actions.xml",
    ],
    "installable": True,
    "application": False,
}
