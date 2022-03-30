# -*- coding: utf-8 -*-
{
    'name': 'Consumable Material Transfer',
    'category': 'Inventory',
    'sequence': 1,
    'version': '15.0.1.0.0',
    'license': 'LGPL-3',
    'summary': """Consumable Material Transfer""",
    'description': """Consumable Material Transfer""",
    'author': 'K.P',
    'depends': ['stock','account', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/consumable_material_view.xml',
        'views/stock_analytic_setting_view.xml',
    ],
    'installable': True,
    'application': True,
}
