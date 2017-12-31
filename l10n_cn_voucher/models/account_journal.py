# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License OPL or later (http://www.gnu.org/licenses/opl.html).

from openerp import models, fields, api, SUPERUSER_ID


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    voucher_type = fields.Selection([('post', '记账凭证'), ('tranfer', '转账凭证'), ('receipt', '收款凭证'),
                                     ('payment', '付款凭证')], string='凭证类型', default='post')

    def init(self, cr):
        try:
            account_journal_obj = self.pool.get('account.journal')
            ids = account_journal_obj.search(cr, SUPERUSER_ID, [('voucher_type','=',None)])
            account_journal_obj.write(cr, SUPERUSER_ID, ids, {'voucher_type': 'post'})
        except:
            pass
