# -*- coding: utf-8 -*-

{
    'name': "Account - Landed Cost error",
    'summary': "Account - Landed Cost error",
    'description': "Account - Landed Cost error",
    'version': "1.0",
    'category': "Accounting/Accounting",
    'author': "Aneesh",
    'license': 'LGPL-3',
    'depends': [
        'account','stock_landed_costs'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/invoice_view.xml',
    ],
    'application': False,
    'installable': True,
}
