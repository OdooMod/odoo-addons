# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomk.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Base Race',
    'summary': 'Base Race',
    'version': '1.0',
    'category': 'Base',
    'summary': """
Base
""",
    'author': "Jarvis (www.odoomk.com)",
    'website': 'http://www.odoomk.com',
    'license': 'AGPL-3',
    'depends': ['base'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/race_views.xml',
        'views/partner_views.xml'
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
}
