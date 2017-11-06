# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomk.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Tiny Inventory Management',
    'version': '1.0',
    'category': 'Warehouse',
    'summary': 'Inventory, Logistics, Warehousing',
    'description': """
Tiny Edtition of Odoo Inventory Management
""",
    'author': "Jarvis (www.odoomk.com)",
    'website': 'http://www.odoomk.com',
    'license': 'LGPL-3',
    'depends': ['stock',
                ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'data': [
        'security/tiny_stock_security.xml',
        'security/ir.model.access.csv',
        'views/tiny_stock_menu_views.xml',
        'views/tiny_stock_picking_views.xml',
        'views/tiny_stock_move_views.xml',
        'views/tiny_stock_inventory_views.xml',


    ],
    'qweb': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
