# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""
purcharse order import wizard
"""
import os
import base64
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime, timedelta
import sys
import time
import openerp.addons.ebiz_cn.top.api
import json

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

class ebiz_shop_account_wizard(osv.osv_memory):
    _name = "ebiz.shop.account.wizard"
    _description = u"导入支付宝对账单"

    def _get_date_start(self, cr, uid, context=None):
        now_time = time.strftime('%Y-%m-%d %H:%M:%S')
        date_start = (datetime.strptime(str(now_time),'%Y-%m-%d %H:%M:%S',) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        return date_start
        
    _columns = {
        'shop_id': fields.many2one('ebiz.shop', string=u"店铺", required=True),
        'date_start': fields.datetime(u'开始时间', required=True),
        'date_end': fields.datetime(u'结束时间', required=True),
    }

    _defaults = {
        'date_start':_get_date_start,
        'date_end': lambda obj, cr, uid, context: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    def import_lines(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        bank_obj = self.pool.get('res.partner.bank')
        active_ids = context.get('active_ids',False)
        res = []
        obj = self.browse(cr, uid, ids[0], context=context)
        #res = self.pool.get('ebiz.shop').search_invoices(cr, uid, [obj.shop_id.id], obj.date_start, obj.date_end, context=context)
        res = [
                {
                    "balance":"100.00",
                    "memo":"hello world",
                    "alipay_order_no":"2014081021001001540010396144",
                    "opt_user_id":"20880063000888880133",
                    "merchant_order_no":"T200P765216671818695",
                    "create_time":"2014-08-20 20:40:03",
                    "self_user_id":"20880063000888880122",
                    "business_type":"PAYMENT",
                    "out_amount":"50.00",
                    "type":"PAYMENT",
                    "in_amount":"50.00"
                }
            ]
        for bank in self.pool.get('account.bank.statement').browse(cr, uid, active_ids, context=context):
            line_ids = []
            for r in res:
                amount = 0
                partner_ids = False
                bank_account_ids = bank_obj.search(cr, uid, [('acc_number','=',str(r.get('opt_user_id', '')).strip())],)
                if bank_account_ids:
                    bank_account_ids = bank_account_ids[0]
                    partner_ids = bank_obj.browse(cr, uid, bank_account_ids).partner_id.id
                else:
                    bank_account_id = False
                if r.get('in_amount',0):
                    amount = r.get('in_amount')
                if r.get('out_amount',0):
                    amount = r.get('out_amount')
                line_vals = {
                    'date': r.get('create_time'),
                    'name': r.get('memo'),
                    'ref':r.get('alipay_order_no'),
                    'partner_id': partner_ids,
                    'amount': amount,
                    'bank_account_id':bank_account_ids,
                }
                line_ids.append((0, 0, line_vals))
            bank.write({'line_ids':line_ids})
            return {
                'name': '支付宝对账记录',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.bank.statement',
                'type': 'ir.actions.act_window',
                'res_id': bank.id,
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
