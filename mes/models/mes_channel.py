# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class MesChannel(models.Model):
    _name = 'mes.channel'
    _description = 'Manufacturing Execution System Channel'

    name = fields.Char('Name')
    protocol = fields.Selection([('modbus', 'Modbus'), ('opc', 'OPC')], string='Protocol')
    item_ids = fields.One2many('mes.item', 'channel_id', string='Items', copy=False)

    serial_port = fields.Integer('Serial Port')
    serial_buad_rate = fields.Selection([('300', '300'), ('600', '600'), ('1200', '1200'), ('2400', '2400'),
                                         ('4800', '4800'), ('9600', '9600'), ('14400', '14400'),
                                         ('19200', '19200'), ('28800', '28800'), ('38400', '38400'),
                                         ('56000', '56000'), ('57600', '57600'), ('115200', '115200'),
                                         ('128000', '128000'), ('256000', '256000')], string='Serial Buad Rate')
    serial_data_bits = fields.Selection([('5', '5'), ('6', '6'), ('7', '7'), ('8', '8')], string='Serial Data Bits')
    serial_parity = fields.Selection([('none', 'None'), ('odd', 'Odd'), ('even', 'Even')], string='Serial Parity')
    serial_stop_bits = fields.Selection([('1', '1'), ('2', '2')], string='Serial Stop Bits')

    opc_prog_id = fields.Char('OPC Prog ID')
    opc_remote_machine_name = fields.Char('OPC Remote Machine Name')
    opc_connection_type = fields.Selection([('inproc', 'InProc'), ('local', 'Local'), ('any', 'Any')])

    @api.multi
    def connection_test(self):
        pass
