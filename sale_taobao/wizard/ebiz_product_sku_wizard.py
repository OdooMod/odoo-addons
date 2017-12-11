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
import time
from datetime import datetime, timedelta
import openerp.addons.decimal_precision as dp
import sys
import openerp.addons.ebiz_cn.top.api
import json
import logging

_logger = logging.getLogger(__name__)

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

class ebiz_product_sku_wizard(osv.osv_memory):
    _name = "ebiz.product.sku.wizard"
    _description = u"商品匹配"
    
    _columns = {
        'date_start': fields.datetime(u'修改时间(开始)', ),
        'date_end': fields.datetime(u'修改时间(结束)', ),
        'shop_id': fields.many2one('ebiz.shop', string=u"店铺", required=True),
        'name': fields.char(u'品名',),
        'product_ids': fields.one2many('ebiz.product.sku.line.wizard','product_id',u'商品列表'),
    }

    _defaults = {

    }
    
    def default_get(self, cr, uid, fields, context=None):
        if context == None:
            context = {}
        res = super(ebiz_product_sku_wizard, self).default_get(cr, uid, fields, context=context)
        res['product_ids'] = context.get('product_ids',False)
        if context :
            if context.get('date_start', False):
                res['date_start'] = context.get('date_start', False)
            if context.get('date_end', False):
                res['date_end'] = context.get('date_end', False)
            res['name'] = context.get('name', False)
            res['shop_id'] = context.get('shop_id', False)
        return res

    def search_product_sku(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context= context)
        context.update({'date_start':obj.date_start,'date_end':obj.date_end,'shop_id':obj.shop_id.id,'name':obj.name})
        products = self.pool.get('ebiz.shop').search_product(cr, uid, [obj.shop_id.id], obj.name, obj.date_start, obj.date_end, context=context)
        res = []
        for product in products:
            out_code = ''
            if product.get('outer_id'):
                out_code = product.get('outer_id')
            product_vals = { 
                'out_code':str(out_code), 
                'num_code':str(product.get('num_iid')), 
                'name': product.get('title'),
                'date_modified': product.get('modified'),
            }
            res.append(product_vals)
        context.update({'product_ids':res})
        return {
                'name': u'商品搜索结果',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ebiz.product.sku.wizard',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'context': context
        }

    def import_product(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context= context):
            self.pool.get('ebiz.shop').import_product(cr, uid, [obj.shop_id.id], obj.product_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}


class ebiz_product_sku_line_wizard(osv.osv_memory):
    _name = "ebiz.product.sku.line.wizard"
    _description = u"商品匹配列表"
    _columns = {
        'out_code': fields.char(u'商家外部编码'),
        'num_code': fields.char(u'商品数字编码'),
        'name': fields.char(u'商品名称'),
        'date_modified': fields.datetime(u'修改时间', ),
        'product_id': fields.many2one('ebiz.product.sku.wizard',u'商品匹配'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
