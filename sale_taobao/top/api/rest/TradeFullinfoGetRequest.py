'''
Created by auto_sdk on 2015.09.17
'''
from openerp.addons.ebiz_cn.top.api.base import RestApi
class TradeFullinfoGetRequest(RestApi):
	def __init__(self,domain='gw.api.taobao.com',port=80):
		RestApi.__init__(self,domain, port)
		self.fields = None

	def getapiname(self):
		return 'taobao.trade.fullinfo.get'
