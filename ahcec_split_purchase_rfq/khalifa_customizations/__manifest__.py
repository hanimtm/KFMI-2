# -*- coding: utf-8 -*-
{
    'name': 'KH Project - Customizations',
    'category': 'Sales',
    'sequence': 1,
    'version': '15.0.1',
    'license': 'LGPL-3',
    'summary': """KH Project - Customizations""",
    'description': """KH Project - Customizations""",
    'author': 'Aneesh.AV',
    'depends': ['product', 'account', 'sale', 'sale_management', 'mrp',
                'account_accountant', 'mail', 'contacts', 'stock', 'purchase',
                'stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/partner_data.xml',
        'data/bom_sequence_data.xml',
        'data/mail_template_data.xml',
        'data/mrp_data.xml',
        'wizard/import_components_view.xml',
        'views/product_view.xml',
        'views/sale_view.xml',
        'views/sec_wh_view.xml',
        'views/bom_request_view.xml',
        'views/bom_dummy_view.xml',
        'views/product_group.xml',
        'views/account_view.xml',
        'views/discount_config_view.xml',
        'views/invoice_view.xml',
        'wizard/bom_request_assign_view.xml',
        'views/bom_view.xml',
        'views/custom_routing_workcenter.xml',
        'views/mrp_routing_view.xml',
        'views/mrp_production_view.xml',
        'views/purchase_view.xml',
        'views/menu_view.xml',
        'views/stock_view.xml',
        'views/company_view.xml',
    ],
    'installable': True,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
