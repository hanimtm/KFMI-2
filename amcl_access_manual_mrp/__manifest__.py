# -*- coding: utf-8 -*-
#################################################################################

{
    'name': "Access Manual MRP",
    'author': "Acespritech Solutions Pvt. Ltd.",
    'summary': """Access Rights to manage manual manufacturing.""",
    'license': 'AGPL-3',
    'description': """
    with this access user can able to create manually Manufacturing Record.
    """,
    'version': '15.0.1.0',
    'depends': ['mrp'],
    'data': [
        'security/security_data.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
