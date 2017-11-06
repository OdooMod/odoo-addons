# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class TinyStockMove(models.Model):
    _name = "tiny.stock.move"
    _description = "Stock Move"
    _order = 'tiny_picking_id, sequence, id'

    name = fields.Char('Description', index=True, required=True)
    sequence = fields.Integer('Sequence', default=10)
    create_date = fields.Datetime('Creation Date', index=True, readonly=True)
    date = fields.Datetime(
        'Date', default=fields.Datetime.now, index=True, required=True,
        states={'done': [('readonly', True)]},
        help="Move date: scheduled date until move is done, then date of actual move processing")
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('stock.move'),
        index=True, required=True)
    date_expected = fields.Datetime(
        'Expected Date', default=fields.Datetime.now, index=True, required=True,
        states={'done': [('readonly', True)]},
        help="Scheduled date for the processing of this move")
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[('type', 'in', ['product', 'consu'])], index=True, required=True,
        states={'done': [('readonly', True)]})

    product_uom_qty = fields.Float(
        'Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        default=1.0, required=True, states={'done': [('readonly', True)]},
        help="This is the quantity of products from an inventory "
             "point of view. For moves in the state 'done', this is the "
             "quantity of products that were actually moved. For other "
             "moves, this is the quantity of product that is planned to "
             "be moved. Lowering this quantity does not generate a "
             "backorder. Changing this quantity on assigned moves affects "
             "the product reservation, and should be done with care.")
    product_qty = fields.Float(
        'Real Quantity', compute='_compute_product_qty', inverse='_set_product_qty',
        digits=0, store=True,
        help='Quantity in the default UoM of the product')
    product_uom = fields.Many2one(
        'product.uom', 'Unit of Measure', required=True, states={'done': [('readonly', True)]})
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template',
        related='product_id.product_tmpl_id',
        help="Technical: used in views")
    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        auto_join=True, index=True, required=True, states={'done': [('readonly', True)]},
        help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations.")
    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location',
        auto_join=True, index=True, required=True, states={'done': [('readonly', True)]},
        help="Location where the system will stock the finished products.")

    partner_id = fields.Many2one(
        'res.partner', 'Destination Address ',
        states={'done': [('readonly', True)]},
        help="Optional address where goods are to be delivered, specifically used for allotment")
    tiny_picking_id = fields.Many2one('tiny.stock.picking', 'Transfer Reference', index=True,
                                 states={'done': [('readonly', True)]})
    note = fields.Text('Notes')
    state = fields.Selection([
        ('draft', 'New'), ('cancel', 'Cancelled'),
        ('done', 'Done')], string='Status',
        copy=False, default='draft', index=True, readonly=True,
        help="* New: When the stock move is created and not yet confirmed.\n"
             "* Done: When the shipment is processed, the state is \'Done\'.")
    origin = fields.Char("Source Document")
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type')
    tiny_inventory_id = fields.Many2one('tiny.stock.inventory', 'Inventory')

    @api.one
    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_product_qty(self):
        if self.product_uom:
            rounding_method = self._context.get('rounding_method', 'UP')
            self.product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id, rounding_method=rounding_method)

    @api.model
    def create(self, vals):
        # TDE CLEANME: why doing this tracking on picking here ? seems weird
        perform_tracking = not self.env.context.get('mail_notrack') and vals.get('tiny_picking_id')
        if perform_tracking:
            picking = self.env['tiny.stock.picking'].browse(vals['tiny_picking_id'])
            initial_values = {picking.id: {'state': picking.state}}
        vals['ordered_qty'] = vals.get('product_uom_qty')
        res = super(TinyStockMove, self).create(vals)
        if perform_tracking:
            picking.message_track(picking.fields_get(['state']), initial_values)
        return res

    @api.onchange('product_id', 'product_qty')
    def onchange_quantity(self):
        if not self.product_id or self.product_qty < 0.0:
            self.product_qty = 0.0
        if self.product_qty < self._origin.product_qty:
            return {'warning': _("By changing this quantity here, you accept the "
                                 "new quantity as complete: Odoo will not "
                                 "automatically generate a back order.")}

    @api.onchange('product_id')
    def onchange_product_id(self):
        product = self.product_id.with_context(lang=self.partner_id.lang or self.env.user.lang)
        self.name = product.partner_ref
        self.product_uom = product.uom_id.id
        self.product_uom_qty = 1.0
        return {'domain': {'product_uom': [('category_id', '=', product.uom_id.category_id.id)]}}

    @api.multi
    def action_done(self):
        self.write({'state': 'done', 'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        #pickings.filtered(lambda picking: picking.state == 'done' and not picking.date_done).write({'date_done': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

        return True

    @api.multi
    def action_cancel(self):
        #if any(move.state == 'done' for move in self):
        #    raise UserError(_('You cannot cancel a stock move that has been set to \'Done\'.'))

        self.write({'state': 'cancel'})
        return True

    @api.multi
    def unlink(self):
        if any(move.state not in ('draft', 'cancel') for move in self):
            raise UserError(_('You can only delete draft moves.'))
        return super(TinyStockMove, self).unlink()
