# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomk.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class res_partner(models.Model):
    _inherit = 'res.partner'

    city_id = fields.Many2one('res.country.city', string="城市", domain="[('state_id','=',state_id)]")
    district_id = fields.Many2one('res.country.district', string="区",domain="[('city_id','=',city_id)]")
