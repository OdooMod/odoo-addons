# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-today OSCG (<http://www.zhiyunerp.com>)
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

from openerp.osv import fields,osv

class product_template(osv.osv):
    _inherit = 'product.template'

    _columns = {
        'num_iid': fields.char(u'淘宝数字编码'),
    }

class product_product(osv.osv):
    _inherit = 'product.product'

    _columns = {
        'sku_id': fields.char(u'淘宝SKU_ID'),
    }


class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'digest':fields.char(u'Digest', size=16),
    }

class sale_order(osv.osv):
    _inherit = 'sale.order'

    _columns = {
        'buyer_memo':fields.text(u'买家留言' ),
        'seller_memo':fields.text(u'卖家留言' ),
        'shop_id': fields.many2one('ebiz.shop', string=u"店铺",  readony = True),
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        sale_ids = super(sale_order, self).search(cr, uid, args, offset, limit, order, context, count)
        if context and context.has_key('tb_so_merge'):
            res = {}
            ids = []
            for so in self.pool.get('sale.order').browse(cr,uid,sale_ids):
                shipping_name = so.partner_shipping_id.digest
                if shipping_name:
                    if shipping_name not in res:
                        res[shipping_name] = []
                    res[shipping_name].append(so)
                
            for v in res.values():
                if len(v) >= 2:
                    v.sort(key=lambda x: x.date_order)
                    ids += [x.id for x in v]
            return ids
        return sale_ids


class stock_move(osv.osv):
    _inherit = 'stock.move'

    # 标记电商店铺库存同步表，库位库存发生了变化
    def action_done(self, cr, uid, ids, context=None):
        res = super(stock_move, self).action_done(cr, uid, ids, context=context)
        recs = self.read(cr, uid, ids, ['product_id', 'location_id', 'location_dest_id'], context = context)
        for r in recs:
            self.pool.get('ebiz.stock').set_stock_qty(cr, uid, r['location_id'][0], r['product_id'][0], context=context)
            self.pool.get('ebiz.stock').set_stock_qty(cr, uid, r['location_dest_id'][0], r['product_id'][0], context=context)
        return res
