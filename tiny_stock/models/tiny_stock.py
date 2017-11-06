# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    count_tiny_picking_draft = fields.Integer(compute='_compute_tiny_picking_count')

    @api.multi
    def _compute_tiny_picking_count(self):
        # TDE TODO count picking can be done using previous two
        domains = {
            'count_tiny_picking_draft': [('state', '=', 'draft')],
        }
        for field in domains:
            data = self.env['tiny.stock.picking'].read_group(domains[field] +
                [('state', 'not in', ('done', 'cancel')), ('picking_type_id', 'in', self.ids)],
                ['picking_type_id'], ['picking_type_id'])
            count = dict(map(lambda x: (x['picking_type_id'] and x['picking_type_id'][0], x['picking_type_id_count']), data))
            for record in self:
                record[field] = count.get(record.id, 0)
                
    @api.multi
    def get_action_tiny_picking_tree_ready(self):
        return self._get_action('tiny_stock.action_picking_tree_ready')

    @api.multi
    def get_tiny_stock_picking_action_picking_type(self):
        return self._get_action('tiny_stock.tiny_stock_picking_action_picking_type')
