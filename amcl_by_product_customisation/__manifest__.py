# -*- coding: utf-8 -*-
{
    'name': 'By Product Customisation',
    'author': 'AMCL',
    'category': 'mrp',
    'summary': 'MRP By-Product Customisation',
    'description': '''
        MRP By-Product Customisation
        ''',
    'version': '15.0.1',
    'depends': ['base', 'mrp', 'mrp_account_enterprise'],
    'application': True,
    'data': [
        'views/mrp_production_views.xml',
        'reports/daily_production_report.xml',
        'reports/report_view.xml',
        'reports/mrp_cost_structure.xml',
    ],
    'license': 'LGPL-3',
    'auto_install': False,
    'installable': True,
}
