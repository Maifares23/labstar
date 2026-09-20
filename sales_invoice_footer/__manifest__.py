# -*- coding: utf-8 -*-
{
    "name": "Sales & Invoice Bank Footer",
    "summary": "Adds the company bank account details to the footer of Sale Order and Invoice reports",
    "version": "19.0.1.3.0",
    "category": "Accounting/Accounting",
    "author": "Ahmed Ali",
    "license": "LGPL-3",
    "depends": ["sale", "account"],
    "data": [
        "views/res_partner_bank_views.xml",
        "views/res_config_settings_views.xml",
        "report/paperformat_data.xml",
        "report/report_bank_footer_templates.xml",
        "report/footer_layout_inherit.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
