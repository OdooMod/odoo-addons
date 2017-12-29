# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    voucher_type = fields.Selection([('post', '记账凭证'), ('tranfer', '转账凭证'), ('receipt', '收款凭证'),
                                     ('payment', '付款凭证')], string='凭证类型', default='post')

    @api.model_cr
    def init(self):
        res = super(AccountJournal, self).init()
        self.search([('voucher_type','=',None)]).write({'voucher_type': 'post'})
        return res
