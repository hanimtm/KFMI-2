# -*- coding: utf-8 -*-
{
    'name': 'KH Project - MTO Purchase',
    'category': 'general',
    'sequence': 1,
    'version': '15.0.1',
    'license': 'LGPL-3',
    'summary': """KH Project - MTO Purchase""",
    'description': """KH Project - MTO Purchase""",
    'author': 'Aneesh.AV',
    'depends': ['product', 'account', 'sale', 'sale_management', 'mrp',
                'account_accountant', 'mail', 'contacts', 'stock','purchase', 'purchase_stock',
                'stock'],
    'data': [
        'views/mrp_production.xml',
    ],
    'installable': True,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
