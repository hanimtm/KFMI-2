# -*- coding: utf-8 -*-
{
    'name': "Sale Report Csutomizations",
    'summary': """
         Modify Sale Order Reports""",
    'description': """
        Modify Sale Order Reports
    """,
    'author': "AMCL",
    'version': '15.0.1',
    'license': 'LGPL-3',
    'depends': ['base', 'saudi_vat_invoice_print', 'sale'],
    'data': [
        # 'security/ir.model.access.csv',
        'report/saleorder_report_customizations.xml',
        'views/sale_order.xml',
        'views/company.xml',
    ],
    'assets': {
        'web.report_assets_pdf': [
            'saudi_vat_invoice_print/static/src/scss/**/*',
        ],
        'web.report_assets_common': [
            'saudi_vat_invoice_print/static/src/scss/**/*',
        ],
    }
}