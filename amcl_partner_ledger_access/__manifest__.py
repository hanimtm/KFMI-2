# -*- coding: utf-8 -*-

{
    'name': "Partner Ledger - View Access",
    'summary': "Partner Ledger - View Access",
    'description': "Partner Ledger - View Access",
    'version': "1.0",
    'category': "Accounting/Accounting",
    'author': "Aneesh",
    'license': 'LGPL-3',
    'depends': [
        'account_reports'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/partner.xml',
    ],
    'application': False,
    'installable': True,
}
