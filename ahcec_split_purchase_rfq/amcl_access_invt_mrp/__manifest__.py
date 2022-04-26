# -*- coding: utf-8 -*-
#################################################################################

{
    'name': "Access Extend",
    'author': "Acespritech Solutions Pvt. Ltd.",
    'summary': """Access Rights extended to user have only readonly.""",
    'license': 'AGPL-3',
    'description': """
""",
    'version': '15.0.1.0',
    'depends': ['base','stock','mrp','quality','delivery',
        'khalifa_customizations','sale_stock','purchase_stock',
        'sale_mrp','stock_landed_costs','direct_material_transfer'],
    'data': [
        'security/security_data.xml',
        'security/ir.model.access.csv',
        'views/mrp_work_order_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
