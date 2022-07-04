# -*- coding: utf-8 -*-
{
    'name': 'Saudi Invoice Format',
    'version': '1.0',
    'depends': ['base', 'account'],
    'category': 'Accounting',
    'data': [
        'views/res_company.xml',
        'views/invoice.xml',
        'views/res_partner.xml',
        'reports/report_saudi_invoice3.xml',
    ],
    'assets': {
        'web.report_assets_pdf': [
            'saudi_vat_invoice_print/static/src/scss/**/*',
        ],
        'web.report_assets_common': [
            'saudi_vat_invoice_print/static/src/scss/**/*',
        ],
    },
    'installable': True,
    'application': False,
    "license": "LGPL-3",
}
