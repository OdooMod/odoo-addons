# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    country_id = fields.Many2one('res.country', string='Country of origin')
