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

class ebiz_sale_merge_wizard(osv.osv_memory):
    _name = "ebiz.sale.merge.wizard"
    _description = u"合并发货地址相同的淘宝订单"

    def merge_so(self, cr, uid, ids,context=None):
        sale_obj = self.pool.get('sale.order')
        order_line_obj = self.pool.get('sale.order.line')
        sale_orders = []
        active_ids = context.get('active_ids',[])
        ship_name = False
        min_date_order = False
        min_date_order_so = False
        if len(active_ids)<2:
            raise osv.except_osv(_('Warning'),_('Please select multiple order to merge in the list view.'))
        for so in sale_obj.browse(cr, uid,active_ids,context):
            if so.state == 'done' or so.state == 'cancel' or so.shipped or so.invoiced:
                raise osv.except_osv(_('Warning'), _('You can not merge sale order in done or cancel state !'))
            key = so.partner_shipping_id.digest
            if not ship_name:ship_name = key
            elif ship_name <> key:
                raise osv.except_osv(_('Warning'), _('You can not merge sale order with different shipping address !'))
            if not min_date_order:
                min_date_order = so.date_order
                min_date_order_so = so
            if min_date_order < so.date_order:
                min_date_order_so = so
            sale_orders.append(so)

        merge_so={
            'name': '%smg_%s' % (min_date_order_so.shop_id.code, self.pool.get('ir.sequence').get(cr, uid, 'sale.order') ),
            'shop_id': min_date_order_so.shop_id.id,
            'origin':','.join(map(lambda x: x.name, sale_orders)),
            'date_order': min_date_order_so and min_date_order_so.date_order or False,
            'state': 'draft',
            'partner_id':min_date_order_so and min_date_order_so.partner_id.id or False,
            'partner_invoice_id':min_date_order_so and min_date_order_so.partner_invoice_id and min_date_order_so.partner_invoice_id.id or False,
            'partner_shipping_id':min_date_order_so and min_date_order_so.partner_shipping_id and min_date_order_so.partner_shipping_id.id or False,
            'pricelist_id':min_date_order_so and min_date_order_so.pricelist_id.id or False,
        }
        so_id = sale_obj.create(cr, uid, merge_so)
        for so in sale_orders:
            for ln in so.order_line:
                vals = {
                    'order_id':so_id,
                    'product_id':ln.product_id.id or False,
                    'name':ln.name or '',
                    'product_uom_qty':ln.product_uom_qty or 1.00,
                    'product_uom':ln.product_uom.id or False,
                    'price_unit':ln.price_unit or 0.00,
                    'product_packaging':ln.product_packaging and product_packaging.id or False,
                    'discount':ln.discount or 0.00,
                    'delay':ln.delay or False,
                }
                order_line_obj.create(cr, uid, vals,context=context)
                
            sale_obj.action_cancel(cr,uid,[so.id])
        return {'type': 'ir.actions.act_window_close'}

ebiz_sale_merge_wizard()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
