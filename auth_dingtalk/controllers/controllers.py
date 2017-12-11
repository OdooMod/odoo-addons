# -*- coding: utf-8 -*-
import hashlib
import json
import time
import datetime

from odoo import http
from odoo.http import request
from urllib import quote
import odoo
from odoo.addons.web.controllers.main import ensure_db
from odoo.tools.translate import _
from odoo.addons.web.controllers.main import Home
from ..helper.ding_helper import DingOperation
from odoo.exceptions import ValidationError
from odoo.tools import config


class HqLogin(Home, http.Controller):

    def __init__(self):
        self.dp = DingOperation()

    @http.route('/hq/get_url', type='http', auth="none")
    def get_url(self, **kw):
        appid = self.dp.appid
        old_url = request.params['old_url']
        url = "https://oapi.dingtalk.com/connect/oauth2/sns_authorize?" \
              "response_type=code&scope=snsapi_login&state=STATE&appid=" + appid \
              + "&redirect_uri=" + old_url + "/web/action_login"
        url = quote(url)
        data = json.dumps({"encode_url": url})
        return data

    @http.route('/hq/get_ding_sign_config', type='http', auth="none")
    def get_ding_sign_config(self):
        to_url = config['aliexpress_redirect_uri'] + '/web/login/free'
        nonceStr = 'heqiauto'
        agentId = config['agentid']
        timeStamp = time.time()
        corpId = config['corpid']
        jsapi = request.env['ir.config_parameter'].search([('key', '=', 'ding_jsapi_ticket')], limit=1).value
        plain = "?jsapi_ticket=" + jsapi + "&noncestr=" + nonceStr \
                + "&timestamp=" + str(timeStamp) + "&url=" + to_url
        signature_value = self.dp._do_get(self.dp.signature_url + plain)
        signature = signature_value['signature']
        data = json.dumps({
            'url': to_url,
            'nonceStr': nonceStr,
            'agentId': agentId,
            'corpId': corpId,
            'signature': signature,
            'timeStamp': str(timeStamp)
        })
        return data

    def _do_err_back(self, name, mobile):
        base_location = request.httprequest.url_root.rstrip('/')
        url = "https://oapi.dingtalk.com/robot/send?access_token=" + self.dp.robot_token
        param = json.dumps(
            {
                "msgtype": "markdown",
                "markdown": {
                    "title": "erp用户登录申请",
                    "text": "#### erp用户登录申请\n" +
                            "> 用户名：" + name + "\n\n" +
                            "> 手机号：" + mobile + "\n\n" +
                            "> 申请说明：用户登录erp时由于信息不完整，无法完成登录请求，请管理员完善用户信息\n" +
                            "###### [登录后台管理](" + base_location + "/web)"
                }
            }
        )
        data = self.dp._do_post(url, param)
        if data['errcode'] == 300001:
            return {"errcode": "err", "errmsg": "发送申请消息失败，请再次申请或电话联系管理员"}
        elif data['errcode'] == 0:
            return {"errcode": "ok", "errmsg": "发送申请消息成功，请稍后重新尝试登录。"}

    @http.route('/web/login/debug', type='http', auth="none")
    def web_debug_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            login = request.params['login']
            password = request.params['password']
            check_user = self._check_loginWithPw(login)
            if check_user is not True:
                values['error'] = _("您没有权限使用账号密码登录。")
                return request.render('web.debug_login', values)
            old_uid = request.uid
            uid = request.session.authenticate(request.session.db, login, password)
            if uid is not False:
                request.params['login_success'] = True
                if not redirect:
                    redirect = '/web'
                return http.redirect_with_hash(redirect)
            request.uid = old_uid
            values['error'] = _("Wrong login/password")
        return request.render('web.debug_login', values)

    @http.route('/web/login/free', type='http', auth="none")
    def web_login_free(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if 'ding_app_code' in kw.keys():
            access_token = request.env['ir.config_parameter'].search([('key', '=', 'ding_crop_token')], limit=1).value
            url = self.dp.user_id_bytoken + "?access_token=" + access_token + '&code=' + kw['ding_app_code']
            user_auth = self.dp._do_get(url)
            if user_auth['errmsg'] != 'ok':
                message = u"获取用户身份信息失败"
                return self._do_err_redirect(message)
            user_id = user_auth['userid']
            user_info = self.dp._get_user(access_token, user_id)
            mobile = user_info['mobile']
            unionid = self._get_encrypt_param(user_info['unionid'])
            user = request.env['res.users'].search([('phone_number', '=', mobile), ('ding_unionid', '=', unionid)])
            if user:
                uid = request.session.authenticate(request.session.db, user.login, user.password)
                if uid is not False:
                    request.params['login_success'] = True
                    if not redirect:
                        redirect = '/web'
                    return http.redirect_with_hash(redirect)
            message = u"您还没有绑定账号,请扫码绑定账号并登录"
            return self._do_err_redirect(message)
        return request.render('web.login_free', values)

    @http.route()
    def web_login(self, **kw):
        if request.httprequest.method == 'POST':
            err_values = request.params.copy()
            name = request.params['name']
            mobile = request.params['mobile']
            data = self._do_err_back(name, mobile)
            if data['errcode'] == 'err':
                user_info = {"mobile": mobile, "name": name}
                return self._do_err_redirect(data['errmsg'], user_info)
            elif data['errcode'] == 'ok':
                # return self._do_err_redirect(data['errmsg'])
                err_values['message'] = _(data['errmsg'])
                http.redirect_with_hash('/web/login')
                return request.render('web.ding_login', err_values)
        return request.render('web.ding_login')

    @http.route('/web/action_login', type='http', auth="none")
    def action_ding_login(self, redirect=None, **kw):
        user_info = self.do_login(request)
        if user_info['errcode'] == 'err':
            return self._do_err_redirect(user_info['errmsg'])
        elif user_info['errcode'] == 'ok':
            data = self._do_loginOrSave(request, user_info['errmsg'])
            if data['errcode'] == 'err':
                return self._do_err_redirect(data['errmsg'], user_info['errmsg'])
            elif data['errcode'] == 'again':
                return self._do_err_redirect(data['errmsg'])
            elif data['errcode'] == 'ok':
                return self._do_post_login(user_info['errmsg'], redirect)

    def do_login(self, request):
        tmpcode = request.params['code']
        if not tmpcode:
            return {"errcode": "err", "errmsg": "错误的访问地址，请输入正确的访问地址"}
        access_token = request.env['ir.config_parameter'].search([('key', '=', 'ding_access_token')]).value
        crop_token = request.env['ir.config_parameter'].search([('key', '=', 'ding_crop_token')]).value
        if access_token is not False and crop_token is not False and tmpcode is not False:
            data = self.dp._get_persistent_code(access_token, crop_token, tmpcode)
            if data['errcode'] == 'err':
                return {"errcode": "err", "errmsg": data['errmsg']}
            elif data['errcode'] == 'ok':
                return {"errcode": "ok", "errmsg": data['errmsg']}
        else:
            return {"errcode": "err", "errmsg": "临时码或access_token无效，请重试"}

    def _do_loginOrSave(self, request, data):
        mobile = data['mobile']
        unionid = self._get_encrypt_param(data['unionid'])
        user_info = self._get_user_mobile(request, mobile)
        if not user_info:
            return {"errcode": "err", "errmsg": "当前用户不存在或信息不完整，无法完成登录,请联系管理员。"}
        if user_info is not False and (user_info.ding_unionid is False or user_info.ding_unionid is None
                                      or user_info.ding_unionid == ''):
            self._do_save_unionId(user_info, unionid)
            return {"errcode": "again", "errmsg": "由于您之前未绑定钉钉账号，现已绑定成功，请再次扫码登录。"}
        elif user_info is not False and (user_info.ding_unionid is not False or user_info.ding_unionid is not None
                                      or user_info.ding_unionid != ''):
            return {"errcode": "ok"}

    def _get_user_mobile(self, request, mobile):
        return request.env['res.users'].sudo().search([('phone_number', '=', mobile)], limit=1)

    def _do_save_unionId(self, user_info, unionId):
        return user_info.update({
            'ding_unionid': unionId
        })

    def _do_err_redirect(self, errmsg, user_info=None):
        err_values = request.params.copy()
        if user_info is not None:
            errmsg = errmsg + """
                    <input type="hidden" name="name" value=%s id="name">
                    <input type="hidden" name="mobile" value=%s id="mobile">
                    <button type="submit" class="btn btn-primary">发送请求帮助</button>
                """ % (user_info['name'], user_info['mobile'])
        err_values['error'] = _(errmsg)
        http.redirect_with_hash('/web/login')
        return request.render('web.ding_login', err_values)

    def _do_post_login(self, user_info, redirect):
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        old_uid = request.uid
        mobile = user_info['mobile']
        unionid = self._get_encrypt_param(user_info['unionid'])
        user = self._check_user_ding_info(mobile, unionid)
        if user['errcode'] == 'err':
            return self._do_err_redirect(user['errmsg'], user_info)
        elif user['errcode'] == 'ok':
            user = user['errmsg']
            uid = request.session.authenticate(request.session.db, user.login, user.password)
            if uid is not False:
                request.params['login_success'] = True
                if not redirect:
                    redirect = '/web'
                return http.redirect_with_hash(redirect)
        request.uid = old_uid
        return self._do_err_redirect("用户不存在或用户信息错误，无法完成登录，请联系管理员。")

    def _check_user_ding_info(self, mobile, unionid):
        user = request.env['res.users'].search([('phone_number', '=', mobile), ('ding_unionid', '=', unionid)], limit=1)
        if user and user.password is not False and user.password_crypt is not False \
                and user.login is not False:
            return {"errcode": "ok", "errmsg": user}
        else:
            return {"errcode": "err", "errmsg": "用户信息不完整，请联系管理员后再次登录"}

    def _get_encrypt_param(self, param):
        m = hashlib.md5()
        m.update(param)
        return m.hexdigest()

    def _check_loginWithPw(self, login):
        user = request.env['res.users'].search([('login', '=', login)], limit=1)
        if user and user.loginwithpw is not False:
            return True
        else:
            return False


