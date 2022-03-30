# -*- coding: utf-8 -*-
{
    'name': 'MRP Customisation',
    'author': 'AMCL',
    'category': 'mrp',
    'summary': 'MRP Customisation',
    'description': '''
        MRP Customisation
        ''',
    'version': '15.0.1.0',
    'depends': ['mrp'],
    'application': True,
    'data': [
        'views/mrp_production_views.xml',
        'views/product_view.xml',
    ],
    'license': 'LGPL-3',
    'auto_install': False,
    'installable': True,
}
