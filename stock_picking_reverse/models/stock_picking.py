# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models, _, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def create_reverse(self):
        return_picking_type_id = self.picking_type_id.return_picking_type_id
        if return_picking_type_id:
            vals = {
                'picking_type_id': return_picking_type_id.id,
                'origin': self.name
            }
            picking_id = self.new(vals)
            picking_id.onchange_picking_type()
            for move_line in self.move_lines:
                move_id = move_line.new({'product_id': move_line.product_id.id})
                move_id.onchange_product_id()
                move_id.update({
                    'product_uom_qty': move_line.product_uom_qty,
                    'location_id': move_line.location_dest_id.id,
                    'location_dest_id': move_line.location_id.id})
                picking_id.move_lines += move_id
            vals = picking_id._convert_to_write(picking_id._cache)
            vals_move_lines = []
            for vals_move_line in vals['move_lines']:
                if vals_move_line[0] == 0:
                    vals_move_lines.append(vals_move_line)
            vals['move_lines'] = vals_move_lines
            picking_id = self.create(vals)
            return picking_id

    @api.multi
    def button_reverse(self):
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_all')
        form_view_id = self.env.ref('stock.view_picking_form')
        picking_id = self.create_reverse()
        if picking_id:
            result = {
                'name': action.name,
                'help': action.help,
                'type': action.type,
                'views': [[form_view_id.id, 'form']],
                'target': action.target,
                'context': {},
                'res_model': action.res_model,
                'res_id': picking_id.id
            }
            return result
