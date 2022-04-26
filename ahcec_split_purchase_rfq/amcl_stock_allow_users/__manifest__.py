# -*- coding: utf-8 -*-

{
    'name': 'AMCL Allowed users',
    'author': 'AMCL',
    'category': 'Stock',
    'summary': 'AMCL Allowed users',
    'description': '''
        AMCL Allowed users
                    ''',
    'version': '15.0.1',
    'depends': ['base', 'account', 'stock','purchase'],
    'application': True,
    'data': [
        'security/security.xml',
        'views/stock_picking_type_views.xml',
        'views/account_payment_term_views.xml',
        'views/product_template_views.xml',
        'views/res_users_views.xml',
        'views/stock_warehouse_views.xml',
        # 'views/account_move_views.xml',
    ],
    'license': 'LGPL-3',
    'auto_install': False,
    'installable': True,

}
