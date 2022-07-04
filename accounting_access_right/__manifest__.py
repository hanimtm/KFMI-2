# -*- coding: utf-8 -*-
{
    'name': "Accounting access right",

    'summary': """""",

    'description': """
    """,

    'author': "Ibrahim Kaddour",
    'website': "",

    'category': 'Customizations',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/groups.xml',
        'views/menuitem.xml'
    ],
    'qweb': [],
    # only loaded in demonstration mode
    'demo': [],
}
