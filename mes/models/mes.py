# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class MesChannel(models.Model):
    _name = 'mes.channel'
    _description = 'Manufacturing Execution System Channel'

    name = fields.Char('Name')
    protocol = fields.Selection([('modbus', 'Modbus'),
                                 ('opc', 'OPC')])
    item_ids = fields.One2many('mes.item', 'channel_id', string='Items', copy=False)


class MesItem(models.Model):
    _name = 'mes.item'
    _description = 'Manufacturing Execution System Item'

    name = fields.Char('Name')
    channel_id = fields.Many2one('mes.channel', string='Channel')
    device_id = fields.Many2one('mes.device', string='Device')


class MesDevice(models.Model):
    _name = 'mes.device'
    _description = 'Manufacturing Execution System Device'

    name = fields.Char('Name')
    item_ids = fields.One2many('mes.item', 'device_id', string='Items', copy=False)
