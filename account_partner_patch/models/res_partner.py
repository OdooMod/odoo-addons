# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, _, fields


class res_partner(models.Model):
    _inherit = 'res.partner'

    property_account_payable_id = fields.Many2one(required=False)
    property_account_receivable_id = fields.Many2one(required=False)
