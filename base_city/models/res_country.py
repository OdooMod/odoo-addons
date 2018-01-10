# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomk.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class CountryCity(models.Model):
    _name = "res.country.city"
    _description = "City"
    _order = 'code'

    name = fields.Char(string='名称', required=True, copy=False)
    code = fields.Char(string='代码', copy=False)
    zip = fields.Char(string='邮政编码', copy=False)
    state_id = fields.Many2one('res.country.state', string="州/省")


class CountryDistrict(models.Model):
    _name = "res.country.district"
    _description = "District"
    _order = 'code'

    name = fields.Char(string='名称', required=True, copy=False)
    code = fields.Char(string='代码', copy=False)
    zip = fields.Char(string='邮编', copy=False)

    city_id = fields.Many2one('res.country.city', string="城市")




