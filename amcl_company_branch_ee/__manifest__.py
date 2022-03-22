# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'Multiple Branch/Unit Setup for Company (Enterprise)',
    'category': 'General',
    'summary': 'This module allows to use for multi-branch concept for single or multi company',
    'description': """This module allows to use for multi-branch concept for single or multi company""",
    'author': 'AMCL',
    'version': '1.0.1',
    'depends': ['base', 'sale_management', 'stock', 'purchase', 'account', 'sale_stock',
                'account_reports', 'stock_account'],
    'images': ['static/description/main_screenshot.png'],
    'data': [
        'security/branch_security.xml',
        'security/ir.model.access.csv',
        'views/branch_view.xml',
        'views/res_partner_view.xml',
        'views/search_template_view.xml',
        'views/stock_view.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/account_view.xml',
        'views/mrp_view.xml',
        'views/fleet_vehicle_view.xml',
        'views/product_view.xml',
        'views/res_company_view.xml',
        'report/sale_report_views.xml',
        'report/purchase_report_views.xml',
        'report/account_invoice_report_view.xml',
        'wizard/account_report_common_view.xml',
        'report/sale_report_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'post_init_hook': 'post_init_check',
    'license': 'LGPL-3',

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
