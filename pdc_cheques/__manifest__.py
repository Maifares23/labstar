# -*- coding: utf-8 -*-
{
    'name': "Post Dated Cheques Handling",
    'version': "18.0.0.2",
    'summary': "This modules helps you to manage Post Dated Cheques. cheques management pdc cheques pdc cheque pdc management register post dated checks register PDC PDC payment cheques manage Manage Cheques Manage PDC",
    'category': 'Accounting & Finance',
    'description': """
    This modules helps you to manage Post dated checks.
    Post dated cheques
    manage post dated cheques
    apply post dated checks
    cheques management
    pdc cheques
    pdc cheque
    pdc management
    register post dated checks
    register PDC
    PDC payment
    cheques manage
    Manage Cheques
    Manage PDC 
    """,
    'author': "Qsys IT",
    'website': 'https://qsys.odoo.com/',
    'maintainer': 'Qsys IT',
    'depends': ['account_reports'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'wizard/pdc_payment.xml',
        'views/pdc_payment_view.xml',
        'views/batch_pdc_view.xml',
        'views/reconcile_collection_check_views.xml',
        'views/account_move.xml',
        'views/res_config_settings.xml',
        'views/account_journal.xml',
    ],
    'license': 'OPL-1',
    'price': 80.00,
    'currency': 'EUR',
    "live_test_url": 'https://www.youtube.com/watch?v=Z-DG4CApz5Y',
    'images': ['static/description/Cover.jpeg'],
}
