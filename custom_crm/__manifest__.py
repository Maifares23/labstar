# -*- coding: utf-8 -*-
{
    "name": "Custom CRM Visit Form",
    "summary": "CRM visit forms with dedicated item models per visit type",
    "version": "19.0.1.1.0",
    "category": "Sales/CRM",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["crm", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/crm_visit_form_views.xml",
        "views/crm_visit_form_menus.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
