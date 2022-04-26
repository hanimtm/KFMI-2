# -*- coding: utf-8 -*-
{
    'name': 'Invoice Customizations',
    'category': 'Account',
    'sequence': 5,
    'version': '15.0.1.0',
    'license': 'LGPL-3',
    'summary': """Invoice Customizations""",
    'description': """Invoice Customizations""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'depends': ['base', 'product', 'account', 'sale'],
    'data': [
        'security/security_data.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_view.xml',
        'views/invoice_view.xml',
        'views/register_payment_option_view.xml',
    ],
    'installable': True,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
