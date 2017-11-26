# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Picking Reverse",
    "summary": "Stock Picking Reverse",
    "version": "1.0",
    "category": "Warehouse",
    "website": "http://www.odoomod.com/",
    'description': """
Stock Picking Reverse
""",
    'author': "Jarvis (www.odoomod.com)",
    'website': 'http://www.odoomod.com',
    'license': 'AGPL-3',
    "depends": ['stock'
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    "data": ['views/stock_picking_views.xml'
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
