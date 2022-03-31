# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payment Request',
    'version': '13.0',
    'category': 'Purchase Module',
    'author': 'AMCL',
    'Category':'HR',
    'summary': """
        This Module allows you to manage all type of expenses
    """,
    'description': """
        Payment, Vendor payment, Customer Payment, Request Payment 
        """,
    'depends': [
        'base', 'purchase','account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/data.xml',
        'views/payment_request.xml',
        'report/report.xml',
        'report/payment_request_report.xml',
        'report/report_request_for_payment.xml',

    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
