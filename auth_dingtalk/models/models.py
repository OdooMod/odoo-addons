# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api
from odoo.addons.hq_login.helper.ding_helper import DingOperation

_logger = logging.getLogger(__name__)


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    def get_ding_token(self):
        dp = DingOperation()
        access_token = dp._get_access_token()
        crop_token = dp._get_crop_token()
        if access_token["errcode"] == 'err':
            _logger.warning(access_token['errmsg'])
        if crop_token["errcode"] == "err":
            _logger.warning(crop_token['errmsg'])
        jsapi_ticket = dp._get_jsapi_ticket(crop_token['errmsg'])
        if jsapi_ticket['errcode'] == 'err':
            _logger.warning(jsapi_ticket['errmsg'])
        access_token_value = self.env['ir.config_parameter'].search([('key', '=', 'ding_access_token')])
        crop_token_value = self.env['ir.config_parameter'].search([('key', '=', 'ding_crop_token')])
        jsapi_ticket_value = self.env['ir.config_parameter'].search([('key', '=', 'ding_jsapi_ticket')])
        if access_token_value:
            access_token_value.write({
                'value': access_token['errmsg']
            })
        else:
            access_token_value.create({
                'key': 'ding_access_token',
                'value': access_token['errmsg']
            })
        if crop_token_value:
            crop_token_value.write({
                'value': crop_token['errmsg']
            })
        else:
            crop_token_value.create({
                'key': 'ding_crop_token',
                'value': crop_token['errmsg']
            })
        if jsapi_ticket_value:
            jsapi_ticket_value.write({
                'value': jsapi_ticket['errmsg']
            })
        else:
            jsapi_ticket_value.create({
                'key': 'ding_jsapi_ticket',
                'value': jsapi_ticket['errmsg']
            })


class Users(models.Model):
    _inherit = 'res.users'

    def init(self):
        pass

    phone_number = fields.Char(u'手机号')
    ding_unionid = fields.Char(u'钉钉号')
    loginwithpw = fields.Boolean(u'是否具有账密登录权限')

    @api.multi
    def _set_encrypted_password(self, encrypted):
        self.env.cr.execute(
            "UPDATE res_users SET password_crypt=%s WHERE id=%s",
            (encrypted, self.id))







