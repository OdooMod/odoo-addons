# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.exceptions import except_orm
from odoo.report import report_sxw
from odoo.tools.translate import _
from math import ceil


class AccountMoveReport(models.AbstractModel):
    _name = 'report.l10n_cn_voucher.report_account_move'

    def _paginate(self, items, max_per_page=5):
        """
        分页函数
        items 为要分页的条目们
        max_per_page 设定每页条数
        返回：页数
        """
        count = len(items)
        return int(ceil(float(count) / max_per_page))

    def _get_account_name(self,id):
        account_name = self.env['account.account'].browse(id).name_get()[0]
        #Account move print use Account here:
        return account_name[1]

    def _get_account_partner(self, id, name):
        value = 'account.account,' + str(id)
        partner_prop_acc = self.pool.get('ir.property').search([('value_reference','=',value)], {})
        if partner_prop_acc:
            return name
        else:
            return False

    def _get_exchange_rate(self, line):
        '''
        Exchange rate: Debit or Credit / currency ammount
        Why not get it from currency code + date ?
        '''
        exchange_rate = False
        if line.amount_currency:
            if line.debit > 0:
                exchange_rate = line.debit/line.amount_currency
            if line.credit > 0:
                exchange_rate = line.credit/( -1 * line.amount_currency)
        return exchange_rate

    def _get_unit_price(self, line):
        '''
        Unit price：Debit or Credit / Quantity
        '''
        unit_price = False
        if line.quantity:
            if line.debit > 0:
                unit_price = line.debit/line.quantity
            if line.credit > 0:
                unit_price = line.credit/line.quantity
        return unit_price

    def _rmb_format(self, value):
        """
        将数值按位数分开
        """
        if value < 0.01:
            # 值为0的不输出，即返回12个空格
            return ['' for i in range(12)]
        # 先将数字转为字符，去掉小数点，然后和12个空格拼成列表，取最后12个元素返回
        return (['' for i in range(12)] + list(('%0.2f'%value).replace('.','')))[-12:]

    def _rmb_upper(self, value):
        """
        人民币大写
        来自：http://topic.csdn.net/u/20091129/20/b778a93d-9f8f-4829-9297-d05b08a23f80.html
        传入浮点类型的值返回 unicode 字符串
        """
        rmbmap  = [u"零",u"壹",u"贰",u"叁",u"肆",u"伍",u"陆",u"柒",u"捌",u"玖"]
        unit = [u"分",u"角",u"元",u"拾",u"佰",u"仟",u"万",u"拾",u"佰",u"仟",u"亿",
                u"拾",u"佰",u"仟",u"万",u"拾",u"佰",u"仟",u"兆"]

        nums = map(int,list(str('%0.2f'%value).replace('.','')))
        words = []
        zflag = 0   #标记连续0次数，以删除万字，或适时插入零字
        start = len(nums)-3
        for i in range(start, -3, -1):   #使i对应实际位数，负数为角分
            if 0 != nums[start-i] or len(words) == 0:
                if zflag:
                    words.append(rmbmap[0])
                    zflag = 0
                words.append(rmbmap[nums[start-i]])
                words.append(unit[i+2])
            elif 0 == i or (0 == i%4 and zflag < 3): #控制‘万/元’
                words.append(unit[i+2])
                zflag = 0
            else:
                zflag += 1

        if words[-1] != unit[0]:    #结尾非‘分’补整字
            words.append(u"整")
        return ''.join(words)

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('l10n_cn_voucher.report_account_move')
        docs = self.env[report.model].browse(docids)
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': docs,
            'paginate': self._paginate,
            'account_name': self._get_account_name,
            'account_partner': self._get_account_partner,
            'exchange_rate': self._get_exchange_rate,
            'unit_price': self._get_unit_price,
            'rmb_format': self._rmb_format,
            'rmb_upper': self._rmb_upper,
        }
        res = report_obj.render('l10n_cn_voucher.report_account_move', docargs)
        return res


