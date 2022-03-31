# -*- coding: utf-8 -*-

{
    'name': 'Alemlaq Sale Customisation',
    'author': 'AMCL',
    'category': 'Sales',
    'summary': 'Sales Customisation',
    'description': '''
        Sales Customisation
                    ''',
    'version': '15.0.1',
    'depends': ['sale_management', 'contacts','account_accountant'],
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'views/sale_type_view.xml',
        'views/res_partner_views.xml',
        'wizard/request_invoice_wizard_view.xml',
        'views/sale_order_views.xml',
    ],
    'license': 'LGPL-3',
    'auto_install': False,
    'installable': True,

}
