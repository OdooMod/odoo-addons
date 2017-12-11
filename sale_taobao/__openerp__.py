# -*- encoding: utf-8 -*-

{
    'name': '电商接口通用模块',
    'version': '1.0',
    "category" : "Sales",
    'description': """ 本模块实现：
    1) 淘宝等电商网店的订单导入
    2) 自动将ERP的库存回写到电商网店
    3) 订单的运单号回写到电商网店
    4) 如果买家已签收，自动为订单开Invoice，自动确认，形成应付账款
    5) 自动导入电商网店的对账单
    """,
    'author': 'OSCG',
    'website': 'http://www.odoomod.com',
    'depends': ['sale', 'stock_account', 'delivery'],
    'init_xml': [],
    'data': [
        'security/ir.model.access.csv',
        'wizard/ebiz_check_order_wizard.xml',
        'wizard/ebiz_product_sku_wizard.xml',
        'wizard/ebiz_shop_merge_wizard.xml',
        'wizard/ebiz_shop_account_wizard.xml',
        'wizard/ebiz_stock_sync_wizard.xml',
        'wizard/ebiz_delivery_sync_wizard.xml',
        'base_data.xml',
        'ebiz_data.xml',
        'ebiz_view.xml',
        'ebiz_action.xml', 
     ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'application': True,
}