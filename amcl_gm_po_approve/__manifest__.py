# -*- coding: utf-8 -*-
{
    'name': 'General Manager PO Approve',
    'category': 'Purchase',
    'sequence': 2,
    'version': '15.0.1.0',
    'license': 'LGPL-3',
    'summary': """KH Project - Purchase Approval""",
    'description': """KH Project - Purchase Approval""",
    'depends': ['base', 'purchase'],
    'data': [
        'security/security_data.xml',
        'views/res_config_settings_view.xml',
        'views/purchase_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
