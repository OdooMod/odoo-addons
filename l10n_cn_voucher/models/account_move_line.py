# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    move_state = fields.Selection(string="凭证状态", related='move_id.state')
    approval_uid = fields.Many2one('res.users', string="审核人", related='move_id.approval_uid')
    post_uid = fields.Many2one('res.users', string="记账人", related='move_id.post_uid')
    cashier_uid = fields.Many2one('res.users', string="出纳", related='move_id.cashier_uid')


    @api.multi
    def _compute_move_state(self):
        for rec in self:
            rec.move_state = rec.move_id.state
            rec.check_uid = rec.move_id.check_uid.name
            rec.validate_uid = rec.move_id.validate_uid.name
            rec.cashier_uid = rec.move_id.cashier_uid.name

    @api.multi
    def button_move(self):
        [action] = self.env.ref('account.action_move_journal_line').read()
        [form_view] = self.env.ref('account.view_move_form').read()
        action['res_id'] = self.move_id.id
        action['views'] = [(form_view.get('id', False), 'form')]
        action['view_mode'] = 'form'
        return action
