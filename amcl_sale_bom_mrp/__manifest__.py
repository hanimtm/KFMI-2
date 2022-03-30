# -*- coding: utf-8 -*-

{
    "name" : "Sale line BOM on MRP-Workorder",
    "version" : "15.0.0.0",
    "category" : "",
    'summary': """
    Sale line BOM on MRP-Workorder"    
    """,
    "author": "AMCL",
    'depends' : ['base', 'sale_management','mrp'],
    'data' : [
        'views/mrp_production_view.xml',
    ],
    'qweb': [],
    "auto_install": False,
    "installable": True,
    "license": "LGPL-3",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
