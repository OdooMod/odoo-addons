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

class ebiz_check_order_wizard(osv.osv_memory):
    _name = "ebiz.check.order.wizard"

    def _get_date_start(self, cr, uid, context=None):
        now_time = time.strftime('%Y-%m-%d %H:%M:%S')
        date_start = (datetime.strptime(str(now_time),'%Y-%m-%d %H:%M:%S',) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        return date_start
        
    _columns = {
        'shop_id': fields.many2one('ebiz.shop', string=u"店铺", required=True),
        'order_state': fields.selection([
            ('WAIT_SELLER_SEND_GOODS', u'等待卖家发货'),
            ('WAIT_BUYER_CONFIRM_GOODS', u'等待买家确认收货'),
            ('TRADE_FINISHED', u'交易成功'),
            ('TRADE_CLOSED', u'交易关闭'),
            ], u'订单状态', required=True),
        'date_start': fields.datetime(u'开始时间', required=True),
        'date_end': fields.datetime(u'结束时间', required=True),

        'order_line': fields.one2many('ebiz.check.order.line.wizard','order_id',u'漏单明细'),
    }

    _defaults = {
        'date_start':_get_date_start,
        'date_end': lambda obj, cr, uid, context: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    def default_get(self, cr, uid, fields, context=None):
        if context == None:
            context = {}
        res = super(ebiz_check_order_wizard, self).default_get(cr, uid, fields, context=context)
        if context and context.get('default_line',False):
            res['order_line'] = context.get('default_line',False)
        if context :
            if context.get('date_start', False):
                res['date_start'] = context.get('date_start', False)
            if context.get('date_end', False):
                res['date_end'] = context.get('date_end', False)
            res['shop_id'] = context.get('shop_id', False)
            res['order_state'] = context.get('order_state', False)
        return res

    def search_import_sale_order(self, cr, uid, ids, context=None):
        res = []
        for obj in self.browse(cr, uid, ids, context=context):
            orders = self.pool.get('ebiz.shop').search_import_orders(cr, uid, [obj.shop_id.id], status = obj.order_state, date_start = obj.date_start, date_end = obj.date_end, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def check_sale_order(self, cr, uid, ids, context=None):
        vals = []
        res = []
        for obj in self.browse(cr, uid, ids, context=context):
            orders = self.pool.get('ebiz.shop').search_orders(cr, uid, [obj.shop_id.id], status = obj.order_state, date_start = obj.date_start, date_end = obj.date_end, context=context)
            for order in orders:
                line_vals = {
                    'sale_code': str(order.get('sale_code')), 
                    'tid': str(order.get('tid')), 
                    'date_create': str(order.get('modified')),
                    'amount': float(order.get('total_fee')) or 0,
                    'buyer_nick': order.get('buyer_nick'), 
                }
                res.append(line_vals)
            
            context.update({'default_line': res})
            context.update({'date_start':obj.date_start,'date_end':obj.date_end,'shop_id':obj.shop_id.id,'order_state':obj.order_state})
            return {
                'name': 'Check Order',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ebiz.check.order.wizard',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'context': context
            }

    def import_sale_order(self, cr, uid, ids, context=None):
        res = []
        for obj in self.browse(cr, uid, ids, context=context):
            for line in obj.order_line:
                res.append(line.tid)
            self.pool.get('ebiz.shop').import_orders(cr, uid, [obj.shop_id.id], res, context=context)
        context.update({'default_line': []})
        return {
            'name': 'Check Order',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ebiz.check.order.wizard',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context
        }


class ebiz_check_order_line_wizard(osv.osv_memory):
    _name = "ebiz.check.order.line.wizard"
    _columns = {
        'sale_code': fields.char(u'单号'),
        'tid': fields.char(u'交易单号'),
        'buyer_nick': fields.char(u'买家昵称'),
        'amount': fields.float(u'金额'),
        'date_create': fields.datetime(u'修改时间', required=True),
        'order_id': fields.many2one('ebiz.check.order.wizard',u'漏单'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
