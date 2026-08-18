{
    'name': 'NTS Website Checkout',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Custom website checkout functionality with store pickup',
    'description': """
        This module provides custom website checkout functionality including store pickup option
        that is only available when products are in stock.
    """,
    'author': 'NTS',
    'website': 'https://www.nts.com',
    'depends': [
        'base',
        'website',
        'website_sale',
        'delivery',
    ],
    'data': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
