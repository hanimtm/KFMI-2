# -*- coding: utf-8 -*-
{
    'name': 'Amcl Mixed Payment',
    'category': 'Account',
    'sequence': 5,
    'version': '15.0.1.0',
    'license': 'LGPL-3',
    'summary': """Allow user to Direct Payment with Mixed Payment(Bank and 
    Cash).""",
    'description': """Allow user to Direct Payment with Mixed Payment(Bank and 
    Cash).""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/account_mixed_payment_view.xml',
    ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
