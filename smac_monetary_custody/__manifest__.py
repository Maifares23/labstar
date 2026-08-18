# -*- coding: utf-8 -*-
{
    "name": "Monetary Custody",
    "summary": "Request and reconcile employee cash custody",
    "description": """
Cash custody requests and reconciliation journal entries for construction projects.
Compatible with Odoo 18.
    """,
    "author": "SMAC",
    "website": "https://www.yourcompany.com",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "depends": [
        "account",
        "mail",
        "portal",
        "smac_construction_management",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/request_cash_custody.xml",
        "views/reconcile_custody.xml",
        "views/account_move.xml",
    ],
    "installable": True,
    "application": False,
}
