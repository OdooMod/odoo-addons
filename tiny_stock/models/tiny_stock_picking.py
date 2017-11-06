# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class TinyStockPicking(models.Model):
    _name = "tiny.stock.picking"
    _inherit = ['mail.thread']
    _description = "Transfer"
    _order = "date asc, id desc"

    name = fields.Char(
        'Reference', default='/',
        copy=False, index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    origin = fields.Char(
        'Source Document', index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Reference of the document")
    note = fields.Text('Notes')

    state = fields.Selection([
        ('draft', 'Draft'), ('cancel', 'Cancelled'),
        ('done', 'Done')], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed\n"
             " * Transferred: has been processed, can't be modified or cancelled anymore\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore")
    date = fields.Datetime(
        'Creation Date',
        default=fields.Datetime.now, index=True, track_visibility='onchange',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Creation Date, usually the time of the order")
    location_id = fields.Many2one(
        'stock.location', "Source Location Zone",
        default=lambda self: self.env['stock.picking.type'].browse(
            self._context.get('default_picking_type_id')).default_location_src_id,
        readonly=True,  # required=True,
        states={'draft': [('readonly', False)]})
    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location Zone",
        default=lambda self: self.env['stock.picking.type'].browse(
            self._context.get('default_picking_type_id')).default_location_dest_id,
        readonly=True,  # required=True,
        states={'draft': [('readonly', False)]})
    move_lines = fields.One2many('tiny.stock.move', 'tiny_picking_id', string="Stock Moves", copy=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Picking Type',
        required=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    picking_type_code = fields.Selection([
        ('incoming', 'Vendors'),
        ('outgoing', 'Customers'),
        ('internal', 'Internal')], related='picking_type_id.code',
        readonly=True)
    partner_id = fields.Many2one(
        'res.partner', 'Partner',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('stock.picking'),
        index=True, required=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    product_id = fields.Many2one('product.product', 'Product', related='move_lines.product_id')

    @api.depends('move_lines.state', 'move_lines.tiny_picking_id')
    @api.one
    def _compute_state(self):
        if not self.move_lines:
            self.state = 'draft'
        elif any(move.state == 'draft' for move in self.move_lines):  # TDE FIXME: should be all ?
            self.state = 'draft'
        elif all(move.state in ['cancel', 'done'] for move in self.move_lines):
            self.state = 'done'

    @api.onchange('picking_type_id', 'partner_id')
    def onchange_picking_type(self):
        if self.picking_type_id:
            if self.picking_type_id.default_location_src_id:
                location_id = self.picking_type_id.default_location_src_id.id
            elif self.partner_id:
                location_id = self.partner_id.property_stock_supplier.id
            else:
                customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()

            if self.picking_type_id.default_location_dest_id:
                location_dest_id = self.picking_type_id.default_location_dest_id.id
            elif self.partner_id:
                location_dest_id = self.partner_id.property_stock_customer.id
            else:
                location_dest_id, supplierloc = self.env['stock.warehouse']._get_partner_locations()

            self.location_id = location_id
            self.location_dest_id = location_dest_id
        # TDE CLEANME move into onchange_partner_id
        if self.partner_id:
            if self.partner_id.picking_warn == 'no-message' and self.partner_id.parent_id:
                partner = self.partner_id.parent_id
            elif self.partner_id.picking_warn not in (
            'no-message', 'block') and self.partner_id.parent_id.picking_warn == 'block':
                partner = self.partner_id.parent_id
            else:
                partner = self.partner_id
            if partner.picking_warn != 'no-message':
                if partner.picking_warn == 'block':
                    self.partner_id = False
                return {'warning': {
                    'title': ("Warning for %s") % partner.name,
                    'message': partner.picking_warn_msg
                }}

    @api.model
    def create(self, vals):
        # TDE FIXME: clean that brol
        defaults = self.default_get(['name', 'picking_type_id'])
        if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get('picking_type_id',
                                                                                          defaults.get(
                                                                                                  'picking_type_id')):
            vals['name'] = self.env['stock.picking.type'].browse(
                vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()

        # TDE FIXME: what ?
        # As the on_change in one2many list is WIP, we will overwrite the locations on the stock moves here
        # As it is a create the format will be a list of (0, 0, dict)
        if vals.get('move_lines') and vals.get('location_id') and vals.get('location_dest_id'):
            for move in vals['move_lines']:
                if len(move) == 3:
                    move[2]['location_id'] = vals['location_id']
                    move[2]['location_dest_id'] = vals['location_dest_id']
        return super(TinyStockPicking, self).create(vals)

    @api.multi
    def write(self, vals):
        res = super(TinyStockPicking, self).write(vals)
        # Change locations of moves if those of the picking change
        after_vals = {}
        if vals.get('location_id'):
            after_vals['location_id'] = vals['location_id']
        if vals.get('location_dest_id'):
            after_vals['location_dest_id'] = vals['location_dest_id']
        if after_vals:
            self.mapped('move_lines').filtered(lambda move: not move.scrapped).write(after_vals)
        return res

    @api.multi
    def unlink(self):
        self.mapped('move_lines').unlink()  # Checks if moves are not done
        return super(TinyStockPicking, self).unlink()

    @api.multi
    def action_done(self):
        draft_moves = self.mapped('move_lines').filtered(lambda self: self.state == 'draft')
        draft_moves.action_done()
        return True

    @api.multi
    def action_cancel(self):
        self.mapped('move_lines').action_cancel()
        return True

