# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Product Origin',
    "summary": "Product Origin",
    "version": "1.0",
    "category": "Sales",
    "website": "http://www.odoomod.com/",
    'description': """
Product Origin
""",
    'author': "Jarvis (www.odoomod.com)",
    'website': 'http://www.odoomod.com',
    'license': 'AGPL-3',
    "depends": [
        'product',
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    "data": [
        'views/product_views.xml'
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
