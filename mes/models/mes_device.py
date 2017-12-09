# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class MesDevice(models.Model):
    _name = 'mes.device'
    _description = 'Manufacturing Execution System Device'

    name = fields.Char('Name')
    item_ids = fields.One2many('mes.item', 'device_id', string='Items', copy=False)
