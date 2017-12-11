# -*- coding: utf-8 -*-
"""
Created on 2012-7-3

@author: lihao

我申请的
App Key: 23243114
App Secret: acf655b07eaea311f2129dd429298473 
"""
import top.api
import json

"""
这边可以设置一个默认的appkey和secret，当然也可以不设置
注意：默认的只需要设置一次就可以了

可以用 sandbox_b_01, 密码 taobao1234 登录沙箱环境，进入下述链接获取sessionkey
http://mini.tbsandbox.com/tools/index.htm?spm=a1z0e.6651725.0.79

"""
appkey = 'test'
appsecret = 'test'
sessionkey = '61008257452f1f3a09ffdc19e20cbcbff16fa483b431e092054718218'
url = "gw.api.tbsandbox.com"
port = 80

#top.setDefaultAppInfo("23243114", "acf655b07eaea311f2129dd429298473")
top.setDefaultAppInfo(appkey, appsecret)

"""
使用自定义的域名和端口（测试沙箱环境使用）
a = top.api.UserGetRequest("gw.api.tbsandbox.com",80)

使用自定义的域名（测试沙箱环境使用）
a = top.api.UserGetRequest("gw.api.tbsandbox.com")

使用默认的配置（调用线上环境）
a = top.api.UserGetRequest()

可以在运行期替换掉默认的appkey和secret的设置
a.set_app_info(top.appinfo("appkey","*******"))
"""

req=top.api.rest.TradesSoldGetRequest(url,port)

req.fields="seller_nick,buyer_nick,title,type,created,sid,tid,seller_rate,buyer_rate,status,payment,discount_fee,adjust_fee,post_fee,total_fee,pay_time,end_time,modified,consign_time,buyer_obtain_point_fee,point_fee,real_point_fee,received_payment,commission_fee,pic_path,num_iid,num_iid,num,price,cod_fee,cod_status,shipping_type,receiver_name,receiver_state,receiver_city,receiver_district,receiver_address,receiver_zip,receiver_mobile,receiver_phone,orders.title,orders.pic_path,orders.price,orders.num,orders.iid,orders.num_iid,orders.sku_id,orders.refund_status,orders.status,orders.oid,orders.total_fee,orders.payment,orders.discount_fee,orders.adjust_fee,orders.sku_properties_name,orders.item_meal_name,orders.buyer_rate,orders.seller_rate,orders.outer_iid,orders.outer_sku_id,orders.refund_id,orders.seller_type"

try:
    resp= req.getResponse(sessionkey)
    print(json.dumps(resp, ensure_ascii=False, indent = 4).encode('gb2312'))
    #print(resp)
except Exception,e:
    print(e)
