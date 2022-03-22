# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    'name' : 'Cancel Manufacturing Order',
    'version' : '1.0',
    'author':'Craftsync Technologies',
    'category': 'Manufacturing',
    'maintainer': 'Craftsync Technologies',
   
    'description': """cancel confirmed Manufacturing Order
cancel confirmed Manufacturing Order
cancel confirmed MO
mo cancel
cancel processed Manufacturing Order
cancel processed Manufacturing Order
cancel processed MO
mo cancel
cancel done Manufacturing Order
cancel done Manufacturing Order
cancel done MO
cancel mo

cancel transferred Manufacturing Order
cancel transferred Manufacturing Order
cancel transferred MO

Cancel completed Manufacturing Order
Cancel completed Manufacturing Order
Cancel completed MO

Reset to draft Manufacturing order
Reset to draft Manufacturing order
Reset to draft MO

cancel manufacturing transaction
cancel manufacturing transaction
cancel MO transaction
manufacturing cancel
cancel manufacturing
cancel mrp
Cancel Mrp
cancel manufacture
cancel manufacturing
Cancel Manufacture
Cancel Manufacturing

cancel work orders
cancel inventory moves
cancel work order
cancel inventory move
cancel stock moves
cancel stock move

Cancel Work Orders
Cancel Inventory Moves
Cancel Work Order
Cancel Inventory Move
Cancel Stock Moves
Cancel Stock Move
""",

    'website': 'https://www.craftsync.com/',
    'license': 'OPL-1',
    'support':'info@craftsync.com',
    'depends' : ['mrp','account'],
    'data': [
        'views/res_config_settings_views.xml',
	    'views/view_manufacturing_order.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/main_screen.png'],
    'price': 14.99,
    'currency': 'EUR',

}
