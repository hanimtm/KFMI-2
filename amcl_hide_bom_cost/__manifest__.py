# -*- coding: utf-8 -*-
{
    'name': 'AMCL - Bom Structure Cost',
    'category': 'mrp',
    'sequence': 5,
    'version': '15.0.1.0',
    'license': 'LGPL-3',
    'summary': """
    Hide & Show Bom Structure Cost based on Group
    """,
    'description': """
    Hide & Show Bom Structure Cost based on Group
    """,
    'author': 'AMCL',
    'depends': ['mrp'],
    'data': [
        'security/mrp_security.xml',
        'report/mrp_report_bom_structure.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'amcl_hide_bom_cost/static/src/js/mrp_bom_report.js'
    #     ]
    # },
    'installable': True,
    'application': False,
    "license": "LGPL-3",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
