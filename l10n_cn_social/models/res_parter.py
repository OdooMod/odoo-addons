# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    qq = fields.Date('QQ')
    wechat = fields.Char('微信')
    aliim = fields.Char('阿里旺旺')
    alipay = fields.Char('支付宝')

