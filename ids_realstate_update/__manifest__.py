# -*- coding: utf-8 -*-
{
    'name': "Real state Update",
    'summary': "Real state Update",
    'description': """
        Real state Update
    """,
    'author': "IDS",
    'website': "https://www.yourcompany.com",
    'category': 'Real State',
    'version': '18.1',
    'depends': ['base', 'nthub_realestate'],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'security/record_rule.xml',
        'views/rs_projects.xml',
        'views/res_partner.xml',
        'views/res_company.xml',
        'views/ownership_contract.xml',
        'views/rental_contract.xml',
        'views/contract_down_payment.xml',
        'views/rental_settlement.xml',
        'views/account_move.xml',
        'views/account_payment.xml',
        'views/actions.xml',
        'views/menu.xml',
        'wizard/invoice_wizard.xml',
        'data/data.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         '/ids_realstate_update/static/src/css/styles.css',
    #     ],
    # },
    'demo': [
        'demo/demo.xml',
    ],
}
