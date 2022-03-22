# -*- coding: utf-8 -*-
{
    'name': 'Direct Material Transfer',
    'category': 'Inventory',
    'sequence': 1,
    'version': '15.0.1.0.0',
    'license': 'LGPL-3',
    'summary': """Direct Material Transfer""",
    'description': """Direct Material Transfer""",
    'author': 'Aneesh.AV',
    'depends': ['stock','account'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/direct_material_view.xml',
        'views/stock_expense_setting.xml',
    ],
    'installable': True,
    'application': True,
}
