# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Hierarchy',
    "summary": "Account Hierarchy",
    "version": "1.0",
    "category": "Accounting",
    "website": "http://www.odoomod.com/",
    'description': """
Account Hierarchy
""",
    'author': "Jarvis (www.odoomod.com)",
    'website': 'http://www.odoomod.com',
    'license': 'AGPL-3',
    "depends": [
        'account_accountant',
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    "data": [
        'views/account_account_views.xml',
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
