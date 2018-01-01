# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountAccount(models.Model):
    _inherit = 'account.account'
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'

    parent_id = fields.Many2one(
        'account.account', 'Parent Account', index=True, ondelete='cascade')
    child_ids = fields.One2many('account.account', 'parent_id', 'Contains')
    parent_left = fields.Integer('Left Parent', index=True)
    parent_right = fields.Integer('Right Parent', index=True)