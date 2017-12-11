# -*- coding: utf-8 -*-
{
    'name': "Auth Dingtalk",

    'summary': """
            To provide users with the DingTalk login mode 阿里钉钉登录认证模块
        """,

    'description': """
        To provide users with the DingTalk login mode
    """,

    'author': "zhaohe",
    'website': "http://www.odoomod.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/ding_login.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}