# -*- coding: utf-8 -*-
# Copyright 2014 wangbuke <wangbuke@gmail.com>
# Copyright 2017 OdooMod <jarvis@odoomod.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.addons.report.controllers.main import ReportController
from odoo.addons.web.controllers.main import Reports, serialize_exception
from odoo.http import route


class WebPdfReports(ReportController):
    @route(['/report/preview'], type='http', auth="user")
    def report_download(self, data, token):
        result = super(WebPdfReports, self).report_download(data, token)
        result.headers['Content-Disposition'] = result.headers['Content-Disposition'].replace('attachment', 'inline')
        return result


class PreviewReports(Reports):
    @route('/web/report', type='http', auth="user")
    @serialize_exception
    def index(self, action, token):
        result = super(PreviewReports, self).index(action, token)
        result.headers['Content-Disposition'] = result.headers['Content-Disposition'].replace('attachment', 'inline')
        return result
