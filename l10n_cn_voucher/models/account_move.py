# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License OPL or later (http://www.gnu.org/licenses/opl.html).

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from ..lib import pycnamount

READONLY_STATE = {
    'validate': [('readonly', True)],
    'posted': [('readonly', True)],
    'cancel': [('readonly', True)],
}


class AccountMove(models.Model):
    _inherit = 'account.move'

    attachment_num = fields.Integer("Attachment Number", states=READONLY_STATE)
    post_uid = fields.Many2one('res.users', '记账人', readony=True, copy=False)
    approval_uid = fields.Many2one('res.users', '审核人', readony=True, copy=False)
    cashier_uid = fields.Many2one('res.users', '出纳', readony=True, copy=False)
    amount_chinese = fields.Char(string="大写合计", compute='_compute_amount_chinese')
    voucher_type = fields.Selection(string='凭证类型', related='journal_id.voucher_type', readonly=True, store=True,
                                    copy=False)
    voucher_name = fields.Char('凭证字号', compute='_compute_voucher_name')
    liquidity = fields.Boolean("包含现金流量", compute='_compute_liquidity')
    no = fields.Integer('凭证编号', states=READONLY_STATE, copy=False)
    state = fields.Selection(
        selection=[('draft', 'Unposted'), ('validate', '核准'), ('posted', 'Posted'), ('cancel', '取消')])
    to_check = fields.Boolean(default=True)

    @classmethod
    def _add_field(cls, name, field):
        """
        extend readonly state
        """
        res = super(AccountMove, cls)._add_field(name, field)
        if field.states and field.states.get('posted'):
            field.states.update(READONLY_STATE)
        return res

    @api.multi
    def name_get(self):
        """
        display chinese account voucher name
        """
        result = []
        for r in self:
            result.append((r.id, r.voucher_name))
        return result

    @api.multi
    def _compute_voucher_name(self):
        for r in self:
            if r.journal_id.id:
                selection = r.journal_id[0]._fields['voucher_type'].selection
                name_map = {x[0]: x[1] for x in selection}
                break
        if name_map:
            for r in self:
                voucher_type = unicode(name_map.get(r.voucher_type, ' '))[0]
                r.voucher_name = '%s-%s' % (voucher_type, r.no)

    @api.model
    def _compute_no(self):
        """
        compute voucher no by voucher type
        """
        if self.voucher_type:
            res = self.search_read([('voucher_type', '=', self.voucher_type), ('no', '!=', None)], ['no'], limit=1,
                                   order='no desc')
            if res:
                return res[0].get('no', 0) + 1
            else:
                return 1

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        self.no = self._compute_no()

    @api.multi
    def _compute_liquidity(self):
        for move in self:
            move.liquidity = False
            for move_line in move.line_id:
                if move_line.account_id.type == 'liquidity':
                    move.liquidity = True
                    break

    @api.multi
    def _compute_amount_chinese(self):
        for move in self:
            debit = 0
            credit = 0
            for line in move.line_id:
                debit += line.debit
                credit += line.credit
                move.amount_chinese = pycnamount.amount2cn(debit if debit > 0 else credit, big=True)

    @api.multi
    def button_validate(self):
        for move in self:
            if move.approval_uid.id == False and self.env.user.has_group(
                    'l10n_cn_voucher.group_post_after_approval'):
                raise ValidationError('提示', '凭证需审核才可记账')
            super(AccountMove, move).button_validate()
            move.write({'post_uid': self.env.uid})

    @api.one
    def button_approval(self):
        for move in self:
            if move.state != 'post':
                if move.approval_uid.id == False:
                    if move.create_uid.id == self.env.uid and self.env.user.has_group(
                            'l10n_cn_voucher.group_same_user_approval') != True:
                        raise ValidationError('制单人和审核人不能相同')
                    move.write({'approval_uid': self.env.uid, 'state': 'validate', 'to_check': False})
                else:
                    move.write({'approval_uid': False, 'state': 'draft', 'to_check': True})

    @api.multi
    def button_cashier(self):
        for move in self:
            if move.state != 'post':
                if move.cashier_uid:
                    move.write({'cashier_uid': False})
                else:
                    move.write({'cashier_uid': self.env.uid})
