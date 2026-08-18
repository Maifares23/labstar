# -*- coding: utf-8 -*-
{
    "name": "Advanced Payment",
    "summary": "Register and track advance payments for construction contracts",
    "description": """
Advanced payments linked to construction contracts and contract invoices.
Compatible with Odoo 18.
    """,
    "author": "SMAC",
    "website": "https://www.yourcompany.com",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "depends": ["account", "smac_construction_management"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/advanced_payment_register.xml",
        "views/contract_project.xml",
        "views/account_payment.xml",
        "views/contract_invoice.xml",
    ],
    "installable": True,
    "application": False,
}
