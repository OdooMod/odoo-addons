# -*- encoding: utf-8 -*-
import time
import logging
from openerp import tools
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from openerp.tools.translate import _
from openerp.osv import fields,osv
import json
import hashlib

from openerp.addons.ebiz_cn.top import setDefaultAppInfo
from openerp.addons.ebiz_cn.top.api.rest import ItemsOnsaleGetRequest
from openerp.addons.ebiz_cn.top.api.rest import TradesSoldIncrementGetRequest
from openerp.addons.ebiz_cn.top.api.rest import ItemSkusGetRequest
from openerp.addons.ebiz_cn.top.api.rest import TradesSoldGetRequest
from openerp.addons.ebiz_cn.top.api.rest import TradeGetRequest
from openerp.addons.ebiz_cn.top.api.rest import TradeFullinfoGetRequest
from openerp.addons.ebiz_cn.top.api.rest import AlipayUserAccountreportGetRequest
from openerp.addons.ebiz_cn.top.api.rest import ItemQuantityUpdateRequest
from openerp.addons.ebiz_cn.top.api.rest import LogisticsOfflineSendRequest


_logger = logging.getLogger(__name__)
class ebiz_shop(osv.osv):
    _name = 'ebiz.shop'
    _description = u"电商店铺"

    def _ebiz_platform(self, cr, uid, context=None):
        return self.get_platforms(cr, uid, context = context)
        
    _columns = {
      'name': fields.char(u'店铺名称', size=16, required=True),
      'code': fields.char(u'店铺前缀', size=8, required=True, help = u"系统会自动给该店铺的订单编号、客户昵称加上此前缀。通常同一个平台的店铺，前缀设置成一样"),
      'platform': fields.selection(_ebiz_platform, u'电商平台', required=True, help = u"淘宝、京东等电商平台" ),
      'categ_id': fields.many2one('product.category', string=u"商品默认分类", required=True),
      'warehouse_id': fields.many2one('stock.warehouse', string=u"店铺仓", required=True),
      'journal_id': fields.many2one('account.journal', string=u"默认销售账簿", required=True),
      'post_product_id': fields.many2one('product.product', string=u"邮费", required=True),
      'coupon_product_id': fields.many2one('product.product', string=u"优惠减款", required=True),
      'gift_product_id': fields.many2one('product.product', string=u"赠品", ),

      'appkey': fields.char(u'App Key', ),
      'appsecret': fields.char(u'App Secret', ),
      'sessionkey': fields.char(u'Session Key', ),
      'apiurl': fields.char(u'API URL', ),
      'authurl': fields.char(u'Auth URL', ),
      'tokenurl': fields.char(u'Token URL', ),
    }

    def get_platforms(self, cr, uid, context=None):
        platforms = [('tb', u'淘宝天猫'), ('sb', u'淘宝沙箱'),]
        return platforms

    def search_product(self, cr, uid, ids, product_name = None, start_modified = None, end_modified = None, context=None):
        """
        1) 按商品名称，商品修改时间搜索店铺商品
        2) start_modified、end_modified 都是UTC时间，需要加上8小时传给电商平台
        """
        shop_id = self.browse(cr, uid, ids[0], context= context)
        setDefaultAppInfo(shop_id.appkey, shop_id.appsecret)
        req = ItemsOnsaleGetRequest(shop_id.apiurl, 80)
        req.fields="approve_status,num_iid,title,nick, outer_id, modified"
        if product_name:
            req.q = product_name
        if start_modified:
            start_modified = (datetime.strptime(str(start_modified),'%Y-%m-%d %H:%M:%S',) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            req.start_modified = start_modified
        if end_modified:
            end_modified = (datetime.strptime(str(end_modified),'%Y-%m-%d %H:%M:%S',) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            req.end_modified = end_modified
        
        req.page_no = 1
        req.page_size = 100
        total_get = 0
        total_results = 100
        res = []
        while total_get < total_results:
            resp= req.getResponse(shop_id.sessionkey)
            total_results = resp.get('items_onsale_get_response').get('total_results')
            if total_results > 0:
                res += resp.get('items_onsale_get_response').get('items').get('item')
            total_get += req.page_size
            req.page_no = req.page_no + 1
        #
        # 时间需要减去8小时
        for r in res:
            r['modified'] = (datetime.strptime(r['modified'],'%Y-%m-%d %H:%M:%S',) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        return res

    def create_product(self, cr, uid, product_vals, context = None):
        """
        1) 创建product.template
        2) 如果商品有SKU，创建product.attribute, product.attribute.value，product.attribute.line
        3) 创建product.product
        4) 电商商品、SKU和ERP product.template、product.product的对应关系：
            如果没有SKU，则一个商品对应一个product.template、一个product.product，其中商品数字编码填入 product.template的num_iid，商家外部编码填入product.product的default_code，如果没有商家外部编码，则将num_iid填入default_code
            如果有SKU，则一个商品对应一个product.template，其中商品数字编码填入product.template的num_iid。每个SKU对应一个product.product，SKU的商家外部编码填入product.product的default_code，SKU的sku_id填入product.product的sku_id
        """
        def get_sku_properties(properties_name ):
            """SKU属性值格式  20000:3275069:品牌:盈讯;1753146:3485013:型号:F908;-1234:-5678:自定义属性1:属性值1
            返回结果 {'品牌':盈讯, '型号':F908, '自定义属性1':属性值1}
            """
            res = {}
            try:
                for vals in properties_name.split(';'):
                    v = vals.split(':')
                    res.update({v[2]: v[3] } )
            except Exception, e:
                pass
            return res
        
        product_res = []
        #创建Product Template
        vals_template = {
            'name': product_vals['name'],
            'num_iid': str(product_vals['num_iid']),
            'type': product_vals['type'],
            'categ_id': product_vals['categ_id'],
            'cost_method': 'real',
            'standard_price': 1.0,
        }
        skus = product_vals.get('sku', False)
        if not skus:
            vals_template.update({'default_code': product_vals['default_code'] } )
            prt_ids = self.pool.get('product.product').create(cr, uid, vals_template, context = context)
            return [prt_ids]

        template_ids = self.pool.get('product.template').search(cr, uid, [('num_iid', '=', str(product_vals['num_iid']) )], context=context)
        if not template_ids:
            template_ids = self.pool.get('product.template').create(cr, uid, vals_template, context = context)
        else:
            template_ids = template_ids[0]
        
        #处理商品SKU
        attr_lines = {}
        for sku in skus:
            #创建 product.product
            prt_vals = {
                'default_code': sku['outer_id'],
                'sku_id': str(sku['sku_id']),
                'product_tmpl_id': template_ids,
                'attribute_value_ids': [],
            }
            
            #创建属性和属性值 product.attribute, product.attribute.value, 
            #处理product.template上字段attribute_line_ids，对象product.attribute.line    
            #处理product.product上字段attribute_value_ids
            properties = get_sku_properties(sku['properties_name'] )
            for k in properties:
                attr_ids = self.pool.get('product.attribute').search(cr, uid, [('name', '=', k)], context = context)
                if attr_ids:
                    attr_ids = attr_ids[0]
                else:
                    attr_ids = self.pool.get('product.attribute').create(cr, uid, {'name': k }, context = context)
                    
                attr_val_ids = self.pool.get('product.attribute.value').search(cr, uid, [('name', '=', properties[k]), ('attribute_id', '=', attr_ids)], context = context)
                if attr_val_ids:
                    attr_val_ids = attr_val_ids[0]
                else:
                    attr_val_ids = self.pool.get('product.attribute.value').create(cr, uid, {'name': properties[k], 'attribute_id': attr_ids }, context = context)
                    
                prt_vals['attribute_value_ids'].append( (4, attr_val_ids) )
                if attr_ids not in attr_lines:
                    attr_lines[attr_ids] = {attr_val_ids: True}
                else:
                    attr_lines[attr_ids][attr_val_ids] = True
            
            #创建product.product
            prt_domain = []
            if prt_vals['default_code']:
                prt_domain = [ ('default_code', '=', prt_vals['default_code']) ]
            else:
                prt_domain = [ ('sku_id', '=', str(prt_vals['sku_id'])) ]
            prt_ids = self.pool.get('product.product').search(cr, uid, prt_domain, context = context)
            if prt_ids:
                prt_ids = prt_ids[0]
            else:
                prt_ids = self.pool.get('product.product').create(cr, uid, prt_vals, context = context)
            product_res.append(prt_ids)
        #
        # 重新创建product.attribute.line
        if attr_lines:
            attr_line_ids = self.pool.get('product.attribute.line').search(cr, uid, [('product_tmpl_id', '=', template_ids)], context = context)
            if attr_line_ids:
                self.pool.get('product.attribute.line').unlink(cr, uid, attr_line_ids, context = context)
            for attr in attr_lines:
                attr_line_vals = {
                    'product_tmpl_id':  template_ids,
                    'attribute_id': attr,
                    'value_ids': [],
                }
                for v in attr_lines[attr]:
                    attr_line_vals['value_ids'].append( (4, v) )
                attr_line_ids = self.pool.get('product.attribute.line').create(cr, uid, attr_line_vals, context = context)
        
        return product_res
        
    def import_product(self, cr, uid, ids, product_ids, context=None):
        """
        1) 按商品数字编码，取得商品SKU编码、属性和属性值
        2) 如果该商品没有SKU，且ERP中没有该商品，ERP中直接创建product.product
        3) 如果该商品有SKU，则ERP中创建product.template，且在product.template 上添加 属性和属性值，并且创建该SKU
        4) 电商店铺商品/SKU和ERP产品的对应关系：依次用电商商品/SKU的商家外部编码、商品数字编码、sku_id 匹配ERP产品的default_code, num_iid, sku_id
        5) 返回匹配的产品ids
        """
        port = 80
        shop = self.browse(cr, uid, ids[0], context = context)
        setDefaultAppInfo(shop.appkey, shop.appsecret)
        req = ItemSkusGetRequest(shop.apiurl,port)
        req.fields="sku_id, num_iid, properties, price, status, memo, properties_name, outer_id"
        
        res = []
        for product in product_ids:
            try:
                req.num_iids = product.num_code
                resp= req.getResponse(shop.sessionkey)
                skus = resp.get('item_skus_get_response').get('skus', False)
                product_vals = {
                    'name': product.name,
                    'num_iid': product.num_code,
                    'type': 'product',
                    'categ_id': shop.categ_id.id,
                    'default_code': product.out_code or product.num_code,
                }
                if skus and skus.get('sku', False):
                    product_vals.update({'sku': skus.get('sku', False) })
                ids = self.create_product(cr, uid, product_vals, context = context)
                res += ids
            #一个商品的导入异常不中断其他商品的继续导入
            except Exception, e:
               #写入 同步异常日志
                syncerr = u"店铺【%s】商品【num_iid=%s】导入错误: %s" % (shop.name, product.num_code, e)
                self.pool.get('ebiz.syncerr').create(cr, uid, {'name':syncerr, 'shop_id': shop.id, 'type': 'product', 'state': 'draft' }, context = context )
        return res

    def search_orders(self, cr, uid, ids, status = 'WAIT_SELLER_SEND_GOODS', date_start = None, date_end = None, context=None):
        """
        从电商店铺搜索一定时间区间创建的、指定交易状态的订单
        本方法支持的交易状态有：
            WAIT_SELLER_SEND_GOODS （默认）
            WAIT_BUYER_CONFIRM_GOODS
            TRADE_FINISHED
            TRADE_CLOSED

淘宝订单交易状态
WAIT_BUYER_PAY：等待买家付款
WAIT_SELLER_SEND_GOODS：等待卖家发货
SELLER_CONSIGNED_PART：卖家部分发货
WAIT_BUYER_CONFIRM_GOODS：等待买家确认收货
TRADE_BUYER_SIGNED：买家已签收（货到付款专用）
TRADE_FINISHED：交易成功
TRADE_CLOSED：交易关闭
TRADE_CLOSED_BY_TAOBAO：交易被淘宝关闭
TRADE_NO_CREATE_PAY：没有创建外部交易（支付宝交易）
WAIT_PRE_AUTH_CONFIRM：余额宝0元购合约中
PAY_PENDING：外卡支付付款确认中
ALL_WAIT_PAY：所有买家未付款的交易（包含：WAIT_BUYER_PAY、TRADE_NO_CREATE_PAY）
ALL_CLOSED：所有关闭的交易（包含：TRADE_CLOSED、TRADE_CLOSED_BY_TAOBAO）
        """
        port = 80
        shop = self.browse(cr, uid, ids[0], context = context)
        setDefaultAppInfo(shop.appkey, shop.appsecret)
        req = TradesSoldIncrementGetRequest(shop.apiurl,port)
        req.fields="tid, buyer_nick, created, discount_fee, adjust_fee, post_fee, total_fee, pay_time, end_time, modified, consign_time, receiver_name"
        req.status = status
        if date_start:
            date_start = (datetime.strptime(str(date_start), '%Y-%m-%d %H:%M:%S',) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            req.start_modified = date_start
        if date_end:
            date_end = (datetime.strptime(str(date_end), '%Y-%m-%d %H:%M:%S',) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            req.end_modified = date_end
        
        res = []
        req.page_no = 1
        req.page_size = 100
        
        # 淘宝沙箱环境不支持use_has_next 参数
#        req.use_has_next = True
#        has_next = True
#        while has_next:
#            resp= req.getResponse(shop.sessionkey)
#            trades = resp.get('trades_sold_get_response').get('trades', False)
#            if trades:
#                res += trades.get('trade')
#            req.page_no += 1
#            has_next = resp.get('trades_sold_get_response').get('has_next', False)

        total_get = 0
        total_results = 100
        while total_get < total_results:
            resp= req.getResponse(shop.sessionkey)
            trades = resp.get('trades_sold_increment_get_response').get('trades', False)
            total_results = resp.get('trades_sold_increment_get_response').get('total_results')
            if total_results > 0:
                res += trades.get('trade')
            total_get += req.page_size
            req.page_no = req.page_no + 1

        # 时间需要减去8小时
        # 单号加上店铺前缀
        for r in res:
            r['created'] = (datetime.strptime(r['created'],'%Y-%m-%d %H:%M:%S',) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            r['modified'] = (datetime.strptime(r['modified'],'%Y-%m-%d %H:%M:%S',) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            r['sale_code'] = '%s_%s' % (shop.code, r['tid'])
        
        orders = self.remove_duplicate_orders(cr, uid, res, context=context)
        return orders

    def create_partner_address(self, cr, uid, shop_code, trade, context=None):
        """
        1) 买家昵称和收货地址转变为 ERP的公司和联系人
        2) 判断Partner是否存在，不存在则创建
        3) 判断收货地址是否存在，不存在则创建
        4) 返回找到的，或者新建的 partner_id 和 address_id
        """
        partner_obj = self.pool.get('res.partner')
        partner_name = "%s_%s" % (shop_code,  trade.get('buyer_nick').strip())
        partner_ids = partner_obj.search(cr, uid, [('name','=',partner_name),('is_company','=',True)], context = context )
        if partner_ids:
            partner_ids = partner_ids[0]
            bank_ids = self.pool.get('res.partner.bank').search(cr, uid, [('partner_id','=',partner_ids),('acc_number','=',str(trade.get('alipay_id')).strip())],)
            if not bank_ids:
                bank_vals = self.pool.get('res.partner.bank').onchange_partner_id(cr, uid, [], partner_ids, context=context)['value']
                bank_vals.update({
                    'partner_id':partner_ids,
                    'acc_number':str(trade.get('alipay_id')).strip(),
                    'state': 'bank',
                    'bank_name': u'支付宝',
                    })
                self.pool.get('res.partner.bank').create(cr, uid, bank_vals,)
        else:
            country_id = self.pool.get('res.country').search(cr, uid, [('code', '=', 'CN')], context = context )
            bank_line_vals = {'state': 'bank','acc_number': str(trade.get('alipay_id')).strip(), 'bank_name': u'支付宝', }
            partner_val = {
                'name': partner_name, 
                'is_company': True,
                'customer': True,
                'supplier': False,
                'bank_ids':[(0,0,bank_line_vals)],
                'country_id': country_id and country_id[0],
            }
            partner_ids = partner_obj.create(cr, uid, partner_val, context = context)
        
        #检查收货地址，创建联系人
        #如果 买家昵称、收货人姓名、电话、手机、省份、城市、区县、地址相同，则认为是同一个联系人，否则ERP新建联系人
        addr_digest = "%s:%s:%s:%s:%s:%s:%s:%s" % (partner_name, trade.get('receiver_name', '').strip(), trade.get('receiver_phone', '').strip(), trade.get('receiver_mobile', '').strip(), trade.get('receiver_state', '').strip(), trade.get('receiver_city', '').strip(), trade.get('receiver_district', '').strip(), trade.get('receiver_address', '').strip(), )
        addr_digest = hashlib.md5(addr_digest).digest()
        addr_ids = partner_obj.search(cr, uid, [('digest', '=', addr_digest)], context = context )
        if addr_ids:
            addr_ids = addr_ids[0]
        else:
            country_id = self.pool.get('res.country').search(cr, uid, [('name', '=', '中国')], context = context )
            state_id = country_id and self.pool.get('res.country.state').search(cr, uid, [('name', '=', trade.get('receiver_state', '').strip()), ('country_id', '=', country_id[0]) ], context = context )
            addr_val = {
                'parent_id': partner_ids, 
                'name': trade.get('receiver_name', '').strip(), 
                'phone': trade.get('receiver_phone', '').strip(), 
                'mobile': trade.get('receiver_mobile', '').strip(), 
                'country_id': country_id and country_id[0] , 
                'state_id': state_id and state_id[0], 
                'city': trade.get('receiver_city', '').strip(), 
                'street2': trade.get('receiver_district', '').strip(), 
                'street': trade.get('receiver_address', '').strip(),
                
                'type': 'delivery',
                'digest': addr_digest, 
                'use_parent_address': False,
                'is_company': False,
                'customer': False,
                'supplier': False,
            }
            addr_ids = partner_obj.create(cr, uid, addr_val, context = context)
        
        return [partner_ids, addr_ids]

    def create_order(self, cr, uid, shop, partner_id, address_id, trade, context=None):
        """
        1) 创建订单
        2) 创建明细行
        3) 添加邮费明细行
        4) 添加赠品明细行
        5) 添加优惠券明细行
        """
        order_obj = self.pool.get('sale.order')
        line_obj = self.pool.get('sale.order.line')
        order_val = order_obj.onchange_partner_id(cr, uid, [], partner_id, context=context)['value']
        order_val.update({
            'name': "%s_%s" % (shop.code,  trade.get('tid')),
            'shop_id': shop.id,
            'date_order':  trade.get('pay_time'),      #订单支付时间
            'create_date': trade.get('created'),       #订单创建时间
            'partner_id': partner_id,
            'partner_shipping_id': address_id,
            'warehouse_id': shop.warehouse_id.id,
            'buyer_memo': trade.get('buyer_memo'),
            'seller_memo': trade.get('seller_memo'),
            'picking_policy': 'one',
            'order_policy': 'picking',
            'order_line': [],
        })
        
        orders = trade.get('orders', {}).get('order', [])
        for o in orders:
            prt_domain = [('default_code', '=', o.get('outer_iid', False)  or o.get('num_iid', False))]
            if o.get('sku_id', False):  #有SKU的情况
                if o.get('outer_sku_id', False):
                    prt_domain = [('default_code', '=', o.get('outer_sku_id', False) )]
                else:
                    prt_domain = [('sku_id', '=', o.get('sku_id', False) )]
            product_ids = self.pool.get('product.product').search(cr, uid, prt_domain, context = context )
            
            #如果没有匹配到产品，报同步异常
            if not product_ids:
                syncerr = u"订单导入错误: 匹配不到商品。tid=%s, 商品【%s】, outer_iid=%s, num_iid=%s, outer_sku_id=%s, sku_id=%s " % ( trade.get('tid'), o.get('title', ''), o.get('outer_iid', ''), o.get('num_iid', ''),  o.get('outer_sku_id', ''), o.get('sku_id', '') )
                self.pool.get('ebiz.syncerr').create(cr, uid, {'name':syncerr, 'shop_id':shop.id , 'type': 'order', 'state': 'draft' }, context = context )
                return False
            
            #添加订单明细行
            line_vals = line_obj.product_id_change(cr, uid, [], order_val['pricelist_id'], product_ids[0], qty=o.get('num'), partner_id=partner_id, context=context)['value']
            line_vals.update({'product_id': product_ids[0] , 'price_unit':o.get('price'),  } )
            order_val['order_line'].append( (0, 0, line_vals) ) 
        
        #添加邮费、赠品和优惠券 明细行
        #店家赠品部分
        if shop.gift_product_id:
            line_vals = line_obj.product_id_change(cr, uid, [], order_val['pricelist_id'], shop.gift_product_id.id, qty=1, partner_id=partner_id, context=context)['value']
            line_vals.update({'product_id': shop.gift_product_id.id , 'price_unit': 0.0, } )
            order_val['order_line'].append( (0, 0, line_vals) )
        
        #邮费部分
        if trade.get('post_fee', 0.0) > 0.001:
            line_vals = line_obj.product_id_change(cr, uid, [], order_val['pricelist_id'], shop.post_product_id.id, qty=1, partner_id=partner_id, context=context)['value']
            line_vals.update({'product_id': shop.post_product_id.id , 'price_unit': trade.get('post_fee', 0.0), } )
            order_val['order_line'].append( (0, 0, line_vals) )

        # 优惠减免
        discount_fee = float(trade.get('discount_fee', 0.0) )
        if discount_fee > 0.001:
            line_vals = line_obj.product_id_change(cr, uid, [], order_val['pricelist_id'], shop.coupon_product_id.id, qty=1, partner_id=partner_id, context=context)['value']
            line_vals.update({'product_id': shop.coupon_product_id.id , 'price_unit': - discount_fee, } )
            order_val['order_line'].append( (0, 0, line_vals) )
        
        order_id = order_obj.create(cr, uid, order_val, context = context)
        
        # 如果没有买家留言和卖家留言，自动确认订单
        if not  trade.get('buyer_memo') and not  trade.get('seller_memo'):
            order_obj.action_button_confirm(cr, uid, [order_id], context = context)
        return order_id


    def pull_order(self, cr, uid, ids, tid, context=None):
        """
        1) 取得交易tid信息
        2) ERP中创建交易对应的SO订单
        3) 如果ERP无此买家、发货地址，自动创建对应的Partner对象及联系人
        4) 如果ERP中无此商品，则报同步异常，不同步此tid
        """
        port = 80
        shop = self.browse(cr,uid,ids[0], context = context)
        setDefaultAppInfo(shop.appkey, shop.appsecret)
        try:
            #req = TradeFullinfoGetRequest(shop.apiurl, port)
            req = TradeGetRequest(shop.apiurl, port)
            req.fields="seller_nick,buyer_nick,created,sid,tid,status,buyer_memo,seller_memo,payment,discount_fee,adjust_fee,post_fee,total_fee,pay_time,end_time,modified,received_payment,price,alipay_id,receiver_name,receiver_state,receiver_city,receiver_district,receiver_address,receiver_zip,receiver_mobile,receiver_phone,orders.price,orders.num,orders.iid,orders.num_iid,orders.sku_id,orders.refund_status,orders.status,orders.oid,orders.total_fee,orders.payment,orders.discount_fee,orders.adjust_fee,orders.sku_properties_name,orders.outer_iid,orders.outer_sku_id"
            
            req.tid = long(tid)
            resp = req.getResponse(shop.sessionkey)
            trade =  resp.get('trade_get_response') and resp.get('trade_get_response').get('trade')
            if not trade: return False
            
            trade['created'] = (datetime.strptime(trade['created'], '%Y-%m-%d %H:%M:%S',) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            trade['pay_time'] = (datetime.strptime(trade['pay_time'], '%Y-%m-%d %H:%M:%S',) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            #创建Partner
            partner_id, address_id = self.create_partner_address(cr, uid, shop.code, trade, context = context )
            #创建订单及明细行
            order_id = self.create_order(cr, uid, shop, partner_id, address_id, trade, context = context )
            return order_id
        except Exception,e:
           #写入 同步异常日志
            syncerr = u"店铺【%s】订单【%s】同步错误: %s" % (shop.name, tid, e)
            self.pool.get('ebiz.syncerr').create(cr, uid, {'name':syncerr, 'shop_id': shop.id, 'type': 'order', 'state': 'draft' }, context = context )
            return False

    def import_orders(self, cr, uid, ids, tids, context=None):
        """
        导入 tids 的订单
        LogisticsOfflineSendRequest
        """
        order_ids = []
        for tid in tids:
            order_id = self.pull_order(cr, uid, ids, tid, context = context )
            if order_id:
                order_ids.append(order_id)
        return order_ids


    def remove_duplicate_orders(self, cr, uid, orders, context=None):
        sale_obj = self.pool.get('sale.order')
        submitted_references = [o['sale_code'] for o in orders]
        existing_order_ids = sale_obj.search(cr, uid, [('name', 'in', submitted_references)], context = context)
        existing_orders = sale_obj.read(cr, uid, existing_order_ids, ['name'], context=context)
        existing_references = set([o['name'] for o in existing_orders])
        orders_to_save = [o for o in orders if o['sale_code'] not in existing_references]
        return orders_to_save
        
    def search_import_orders(self, cr, uid, ids, status = 'WAIT_SELLER_SEND_GOODS', date_start = None, date_end = None, context=None):
        """
        搜索订单，批量导入
        """
        port = 80
        shop = self.browse(cr, uid, ids[0], context = context)
        setDefaultAppInfo(shop.appkey, shop.appsecret)
        req = TradesSoldIncrementGetRequest(shop.apiurl,port)
        req.fields="seller_nick,buyer_nick,created,sid,tid,status,buyer_memo,seller_memo,payment,discount_fee,adjust_fee,post_fee,total_fee, pay_time,end_time,modified,received_payment,price,alipay_id,receiver_name,receiver_state,receiver_city,receiver_district,receiver_address, receiver_zip,receiver_mobile,receiver_phone,orders.price,orders.num,orders.iid,orders.num_iid,orders.sku_id,orders.refund_status,orders.status,orders.oid, orders.total_fee,orders.payment,orders.discount_fee,orders.adjust_fee,orders.sku_properties_name,orders.outer_iid,orders.outer_sku_id"
        req.status = status
        if date_start:
            date_start = (datetime.strptime(str(date_start), '%Y-%m-%d %H:%M:%S',) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            req.start_modified = date_start
        if date_end:
            date_end = (datetime.strptime(str(date_end), '%Y-%m-%d %H:%M:%S',) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            req.end_modified = date_end
        
        res = []
        req.page_no = 1
        req.page_size = 100
        
        # 淘宝沙箱环境不支持use_has_next 参数
#        req.use_has_next = True
#        has_next = True
#        while has_next:
#            resp= req.getResponse(shop.sessionkey)
#            trades = resp.get('trades_sold_get_response').get('trades', False)
#            if trades:
#                res += trades.get('trade')
#            req.page_no += 1
#            has_next = resp.get('trades_sold_get_response').get('has_next', False)

        total_get = 0
        total_results = 100
        while total_get < total_results:
            resp= req.getResponse(shop.sessionkey)
            trades = resp.get('trades_sold_increment_get_response').get('trades', False)
            total_results = resp.get('trades_sold_increment_get_response').get('total_results')
            if total_results > 0:
                res += trades.get('trade')
            total_get += req.page_size
            req.page_no = req.page_no + 1

        # 时间需要减去8小时
        # 单号加上店铺前缀
        order_ids = []
        for trade in res:
            trade['created'] = (datetime.strptime(trade['created'], '%Y-%m-%d %H:%M:%S',) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            trade['pay_time'] = (datetime.strptime(trade['pay_time'], '%Y-%m-%d %H:%M:%S',) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            trade['sale_code'] = '%s_%s' % (shop.code, trade['tid'])
        
        orders = self.remove_duplicate_orders(cr, uid, res, context=context)
        for trade in orders:
            try:
                #创建Partner
                partner_id, address_id = self.create_partner_address(cr, uid, shop.code, trade, context = context )
                #创建订单及明细行
                order_id = self.create_order(cr, uid, shop, partner_id, address_id, trade, context = context )
                order_ids.append(order_id)
            except Exception, e:
                #写入 同步异常日志
                syncerr = u"店铺【%s】订单【%s】同步错误: %s" % (shop.name, trade['tid'], e)
                self.pool.get('ebiz.syncerr').create(cr, uid, {'name':syncerr, 'shop_id': shop.id, 'type': 'order', 'state': 'draft' }, context = context )
                continue
        return order_ids


    def _order_offline_send(self, cr, uid, shop, tid, logistics_company, logistics_id, context=None):
        setDefaultAppInfo(shop.appkey, shop.appsecret)
        req = LogisticsOfflineSendRequest(shop.apiurl, 80)
        req.tid = tid
        req.out_sid = logistics_id
        req.company_code = logistics_company
        try: 
           resp = req.getResponse(shop.sessionkey)
        except Exception,e:
           #写入 同步异常日志
            syncerr = u"店铺【%s】订单【%s】物流发货同步错误: %s" % (shop.name, tid, e)
            self.pool.get('ebiz.syncerr').create(cr, uid, {'name':syncerr, 'shop_id': shop.id, 'type': 'delivery', 'state': 'draft' }, context = context )
            return False
        return True

    def orders_offline_send(self, cr, uid, ids, order_ids, context=None):
        """
        订单发货信息更新到电商平台
        """
        order_obj = self.pool.get('sale.order')
        picking_obj = self.pool.get('stock.picking')
        for order in order_obj.browse(cr, uid, order_ids, context = context):
            if not order.shop_id or not order.picking_ids or not order.shipped:
                continue
            shop = order.shop_id
            picking = order.picking_ids[0]
            delivery_code = picking.carrier_tracking_ref
            partner_ref = picking.carrier_id and picking.carrier_id.partner_id.ref
            if not delivery_code or not partner_ref:
                syncerr = u"店铺【%s】订单【%s】物流发货同步错误: 对应的发货单没有运单号，或者没有快递方式，或者快递方式的快递公司（Partner）没有填写’物流公司代码‘（Ref字段）！" % (shop.name, order.name)
                self.pool.get('ebiz.syncerr').create(cr, uid, {'name':syncerr, 'shop_id': shop.id, 'type': 'delivery', 'state': 'draft' }, context = context )
                continue
                
            #tid 格式为 店铺前缀_电商订单编号，如果是合并订单，则格式为 店铺前缀mg_流水号
            i = order.name.find('_')
            if i <= 0: continue
            tid = order.name[i+1:]
            if order.name[:i].endswith('mg'):  #处理合并订单
                if not order.origin:
                    syncerr = u"店铺【%s】订单【%s】物流发货同步错误: 合并订单的源单据中没有原始订单号！" % (shop.name, order.name)
                    self.pool.get('ebiz.syncerr').create(cr, uid, {'name':syncerr, 'shop_id': shop.id, 'type': 'delivery', 'state': 'draft' }, context = context )
                    continue
                tids = order.origin.split(',')
                for t in tids:
                    i = t.find('_')
                    if i <= 0: continue
                    tid = t[i+1:]
                    self._order_offline_send(cr, uid, shop, tid, partner_ref, delivery_code, context=context)
            else:
                self._order_offline_send(cr, uid, shop, tid, partner_ref, delivery_code, context=context)
        return True

    def _order_signed(self, cr, uid, shop, order):
        #tid 格式为 店铺前缀_电商订单编号，如果是合并订单，则格式为 店铺前缀mg_流水号
        signed = True
        setDefaultAppInfo(shop.appkey, shop.appsecret)
        req = TradeGetRequest(shop.apiurl)
        req.fields="tid, modified, consign_time, status"
        
        i = order.name.find('_')
        if i <= 0:
            signed = False
        tid = order.name[i+1:]
        if order.name[:i].endswith('mg'):  #处理合并订单
            if not order.origin:
                syncerr = u"店铺【%s】订单【%s】买家签收同步错误: 合并订单的源单据中没有原始订单号！" % (shop.name, order.name)
                self.pool.get('ebiz.syncerr').create(cr, uid, {'name':syncerr, 'shop_id': shop.id, 'type': 'invoice', 'state': 'draft' }, context = context )
                signed = False
            tids = order.origin.split(',')
            for t in tids:
                i = t.find('_')
                if i <= 0:
                    signed = False
                    continue
                tid = t[i+1:]
                req.tid = long(tid)
                resp = req.getResponse(shop.sessionkey)
                trade =  resp.get('trade_get_response') and resp.get('trade_get_response').get('trade')
                if not trade or trade['status'] != 'TRADE_FINISHED': 
                    signed = False
                    continue
        else:
            req.tid = long(tid)
            resp = req.getResponse(shop.sessionkey)
            trade =  resp.get('trade_get_response') and resp.get('trade_get_response').get('trade')
            if not trade or trade['status'] != 'TRADE_FINISHED': 
                signed = False
        
        return signed
        
    def orders_signed(self, cr, uid, ids, order_ids, context=None):
        """
        1) 检查订单，买家是否签收
        2) 如果买家已签收，则自动开票，并确认发票
        """
        order_obj = self.pool.get('sale.order')
        picking_obj = self.pool.get('stock.picking')
        invoice_obj = self.pool.get('account.invoice')
        port = 80
        res = []
        for order in order_obj.browse(cr, uid, order_ids, context = context):
            if not order.shop_id or not order.shipped or order.invoice_ids:
                continue
            shop = order.shop_id
            try:
                signed = self._order_signed(cr, uid, shop, order)
                if not signed:
                    continue
                picking_ids =  [picking.id for picking in order.picking_ids]
                if not picking_ids:
                    continue
                invoice_ids = picking_obj.action_invoice_create(cr, uid, picking_ids, shop.journal_id.id, context=context)
                if not invoice_ids: continue
                invoice_obj.signal_workflow(cr, uid, invoice_ids, 'invoice_open')
                res += invoice_ids
            except Exception, e:
               #写入 同步异常日志
                syncerr = u"店铺【%s】订单【%s】买家签收同步错误: %s" % (shop.name, tid, e)
                self.pool.get('ebiz.syncerr').create(cr, uid, {'name':syncerr, 'shop_id': shop.id, 'type': 'invoice', 'state': 'draft' }, context = context )
        
        return res


    def search_invoices(self, cr, uid, ids, date_start = None, date_end = None, context=None):
        """
        从电商店铺搜索一定时间区间创建的、指定交易状态的支付宝对账记录。
        支付类型:
            PAYMENT:在线支付，TRANSFER:转账，DEPOSIT:充值，WITHDRAW:提现，
            CHARGE:收费，PREAUTH:预授权，OTHER：其它。
        """
        port = 80
        shop = self.browse(cr, uid, ids[0], context = context)
        setDefaultAppInfo(shop.appkey, shop.appsecret)
        req = AlipayUserAccountreportGetRequest(shop.apiurl,port)
        req.fields=" balance,memo,alipay_order_no,opt_user_id,merchant_order_no,create_time,self_user_id,business_type,out_amount,type,in_amount"
        if date_start:
            date_start = (datetime.strptime(str(date_start),'%Y-%m-%d %H:%M:%S',) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            req.start_time = date_start
        if date_end:
            date_end = (datetime.strptime(str(date_end),'%Y-%m-%d %H:%M:%S',) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            req.end_time = date_end
        
        res = []
        req.page_no = 1
        req.page_size = 100

        total_get = 0
        total_results = 100
        while total_get < total_results:
            resp= req.getResponse(shop.sessionkey)
            trades = resp.get('alipay_user_accountreport_get_response').get('alipay_records', False)
            total_results = resp.get('alipay_user_accountreport_get_response').get('total_results')
            if total_results > 0:
                res += trades.get('alipay_record')
            total_get += req.page_size
            req.page_no = req.page_no + 1

        # 时间需要减去8小时
        for r in res:
            r['create_time'] = (datetime.strptime(r['create_time'],'%Y-%m-%d %H:%M:%S',) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        #测试数据
        # res = [
        #         {
        #             "balance":"100.00",
        #             "memo":"hello world",
        #             "alipay_order_no":"2014081021001001540010396144",
        #             "opt_user_id":"20880063000888880133",
        #             "merchant_order_no":"T200P765216671818695",
        #             "create_time":"2014-08-20 20:40:03",
        #             "self_user_id":"20880063000888880122",
        #             "business_type":"PAYMENT",
        #             "out_amount":"50.00",
        #             "type":"PAYMENT",
        #             "in_amount":"50.00"
        #         }
        #     ]

        return res


class ebiz_stock(osv.osv):
    _name = 'ebiz.stock'
    _description = u"电商店铺库存同步"
    _rec_name = 'product_id'
    _columns = {
      'shop_id': fields.many2one('ebiz.shop', string=u"店铺", required = True),
      'location_id': fields.many2one('stock.location', string=u"店铺库位", required = True),
      'product_id': fields.many2one('product.product', string=u"产品", required = True),
      'sync_date': fields.datetime(string=u"最近同步时间", readonly = True),
      'sync_qty': fields.integer(string=u"最近同步数量", readonly = True),
      'sync_check': fields.boolean(string=u"要否同步", ),
    }

    _location_shop = {}
    def set_stock_qty(self, cr, uid, location_id, product_id, context=None):
        """
        1) 库存发生变化时候，调用此方法更新 店铺库存同步记录
        2) 为了提高更新效率，缓存 库位到店铺的对应关系
        """
        shop_id = self._location_shop.get(location_id, False)
        if shop_id == -1: return False   # 该库位没有对应到店铺
        if not shop_id:
            wh_ids = self.pool.get('stock.warehouse').search(cr, uid, [('lot_stock_id', '=', location_id)], context = context)
            if not wh_ids:
                self._location_shop[location_id] = -1
                return False
            shop_ids = self.pool.get('ebiz.shop').search(cr, uid, [('warehouse_id', '=', wh_ids[0])], context = context)
            if not shop_ids:
                self._location_shop[location_id] = -1
                return False
            self._location_shop[location_id] = shop_ids[0]
            shop_id = self._location_shop.get(location_id, False)

        vals = {
            'shop_id': shop_id,
            'location_id': location_id,
            'product_id': product_id,
            'sync_check': True
        }
        ids = self.search(cr, uid, [('shop_id', '=', shop_id), ('location_id', '=', location_id), ('product_id', '=', product_id)], context = context)
        if ids:
            self.write(cr, uid, ids, vals, context = context)
        else:
            self.create(cr, uid, vals, context = context)
            
        return True


    def sync_stock_qty(self, cr, uid, ids, context=None):
        """
         同步本条记录的库存数量到 电商店铺
        """
        port = 80
        res = self.read_group(cr, uid, [('sync_check', '=', True ), ('id', 'in', ids )], ['shop_id',], ['shop_id' ], context = context)
        for r in res:
            shop = self.pool.get('ebiz.shop').browse(cr, uid, r['shop_id'][0], context=context)
            location_id = shop.warehouse_id.lot_stock_id.id
            setDefaultAppInfo(shop.appkey, shop.appsecret)
            
            line_ids = self.search(cr, uid, r['__domain'], context = context)
            prts = self.read(cr, uid, line_ids, ['product_id'], context = context)
            product_ids = [x['product_id'][0] for x in prts]
            context.update({'location': location_id})
            ss = self.pool.get('product.product')._product_available(cr, uid, product_ids, context=context)
            for product in self.pool.get('product.product').browse(cr, uid, product_ids, context=context):
                req = ItemQuantityUpdateRequest(shop.apiurl, port)
                req.num_iid= long(product.num_iid)
                if product.default_code:
                    req.outer_id = product.default_code
                else:
                    req.sku_id = product.sku_id
                qty = product.virtual_available
                if qty < 0: qty = 0
                req.quantity = int(qty)
                req.type=1
                try: 
                   resp = req.getResponse(shop.sessionkey)
                   ids = self.search(cr, uid, [('shop_id', '=', shop_id), ('product_id', '=', product.id)], context = context )
                   self.write(cr, uid, ids, {'sync_date': time.strftime('%Y-%m-%d %H:%M:%S'), 'sync_check': False, 'sync_qty': qty }, context=context)
                except Exception,e:
                   #写入 同步异常日志
                    syncerr = u"店铺【%s】商品【[%s]%s】库存数量同步错误: %s" % (shop.name, product.default_code, product.name, e)
                    self.pool.get('ebiz.syncerr').create(cr, uid, {'name':syncerr, 'shop_id': shop.id, 'type': 'stock', 'state': 'draft' }, context = context )

        return True


class ebiz_syncerr(osv.osv):
    _name = 'ebiz.syncerr'
    _description = u"电商同步异常"
    _order = "id desc"

    _columns = {
      'create_date': fields.datetime(u'时间', readony = True),
      'name': fields.text(u'错误描述', required=True, readony = True),
      'shop_id': fields.many2one('ebiz.shop', string=u"店铺", required=True, readony = True),
      'type': fields.selection([ ('product', u'商品同步'), ('order', u'订单同步'), ('stock', u'库存同步'), ('delivery', u'运单同步'), ('invoice', u'发票/对账单同步'),], u'错误类型', required=True, readony = True),
      'state': fields.selection([ ('draft', u'未解决'), ('done', u'已解决'),], u'错误状态', required=True, readony = True),
    }
    
    _defaults = {
        'state': 'draft',
    }

    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'}, context = context)
        return True

