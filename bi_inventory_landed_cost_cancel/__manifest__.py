# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Stock Landed Cost Cancel and Reverse",
    "version" : "15.0.0.0",
    "category" : "Warehouse",
    'summary': "Reverse and Cancel Landed Cost cancel landed cost reset landed cost cancel stock landed cost cancel inventory landed cost reverse landed cost reset landed cost reverse stock landed cost reset stock landed cost reset to draft landed cost revert landed cost",
    "description": """
    
            Inventory Landed Cost Cancel in odoo,
            Reverse and Cancel Landed Cost in odoo,
            Cancel landed cost in odoo,
            reverse landed cost in odoo,
            reset landed cost in odoo,
            recompute landed cost in odoo,   

    """,
    'license':'OPL-1',
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.in",
    "price": 15,
    "currency": 'EUR',
    "depends" : ['account','purchase','stock','stock_landed_costs'],
    "data": [
        "views/stock_landed_cost_inherit_views.xml",  
    ],
    "qweb" : [],
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/NOsxZidZyo8',
    "images":["static/description/Banner.png"],
}
