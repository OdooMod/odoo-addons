# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License APL-3.0 or later (http://www.gnu.org/licenses/apl.html).

{
    'name': 'Base City',
    "summary": "Base City",
    "version": "1.0",
    "category": "Hidden",
    "website": "http://www.odoomod.com/",
    'description': """
Base City
""",
    'author': "Jarvis (www.odoomod.com)",
    'website': 'http://www.odoomod.com',
    'license': 'AGPL-3',
    "depends": [
        'base'
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    "data": [
       'views/res_country_views.xml',
       'views/res_partner_views.xml',
       'views/res_country_menus.xml',
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
