# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': '中国会计财务凭证',
    "summary": "Account Voucher",
    "version": "1.0",
    "category": "Localization",
    "website": "http://www.odoomod.com/",
    'description': """
Account Voucher
""",
    'author': "Jarvis (www.odoomod.com)",
    'website': 'http://www.odoomod.com',
    'license': 'AGPL-3',
    "depends": [
        'account_accountant','account_cancel','account_period','account_hierarchy'
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    "data": [
        'security/account_security.xml',
        'views/account_config_views.xml',
        'views/account_journals_views.xml',
        'views/account_move_views.xml',
        'views/account_move_line_views.xml',
        'views/account_account_views.xml',
        'report/account_move_report.xml'
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
