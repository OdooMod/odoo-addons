# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'MES',
    "summary": "Manufacturing Execution System",
    "version": "0.1",
    "category": "Manufacturing",
    "website": "http://www.odoomod.com/",
    'description': """
Odoo MES (Manufacturing Execution System)

Experimental version

""",
    'author': "Jarvis (www.odoomod.com)",
    'website': 'http://www.odoomod.com',
    'license': 'AGPL-3',
    "depends": [
        'base',
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    "data": [
        'security/ir.model.access.csv',
        'views/mes_menu_views.xml',
        'views/mes_channel_views.xml',
        'views/mes_device_views.xml',
        'views/mes_item_views.xml',
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
