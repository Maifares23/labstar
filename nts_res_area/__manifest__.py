{
    'name': 'NTS Res Area',
    'version': '1.0',
    'summary': 'Module for managing residential areas',
    'description': 'This module provides features to manage residential areas in the Normandy system.',
    'author': 'Ahmed Elkady',
    'website': 'http://www.yourcompany.com',
    'category': 'Custom',
    'depends': ['base','web','website_sale', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_area_views.xml',
        'views/res_partner_views.xml',
        'views/template.xml',
        'views/res_country_state_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'nts_res_area/static/src/js/website_sale_address_extend.js',
            # 'nts_res_area/static/src/xml/collect_availability.xml',
        ],
    },

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}