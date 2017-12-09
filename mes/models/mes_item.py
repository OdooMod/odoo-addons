# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class MesItem(models.Model):
    _name = 'mes.item'
    _description = 'Manufacturing Execution System Item'

    name = fields.Char('Name')
    channel_id = fields.Many2one('mes.channel', string='Channel')
    device_id = fields.Many2one('mes.device', string='Device')

    @api.multi
    def poll(self):
        pass
