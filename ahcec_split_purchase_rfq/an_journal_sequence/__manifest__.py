# -*- coding: utf-8 -*-

{
    'name': 'Journal Sequence For Odoo 15',
    'version': '15.1.0',
    'category': 'Accounting',
    'summary': 'Journal Sequence For Odoo 15',
    'sequence': '1',
    'author': 'Aneesh.AV',
    'depends': ['account'],
    'demo': [],
    'data': [
        'data/account_data.xml',
        'views/account_journal.xml',
        'views/account_move.xml',
    ],
    'qweb': [],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
}
