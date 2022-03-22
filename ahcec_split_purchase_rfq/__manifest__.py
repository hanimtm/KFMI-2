# -*- coding: utf-8 -*-
#################################################################################

{
    'name': "Split Purchase RFQ",
    'author': "Aneesh.AV",
    'category': 'purchase',
    'summary': """Split purchase RFQ""",
    'license': 'AGPL-3',
    'description': """
""",
    'version': '15.0.1.0',
    'depends': ['base','purchase'],
    'data': [
        'security/allow_split_purchase_rfq.xml',
        'views/purchase_order_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
