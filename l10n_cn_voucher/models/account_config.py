# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    group_post_after_approval = fields.Boolean("凭证审核后才能记账",implied_group="l10n_cn_voucher.group_post_after_approval")
    group_same_user_approval = fields.Boolean("制单人和审核人可为同一人",implied_group="l10n_cn_voucher.group_same_user_approval")

    module_l10n_cn_reports = fields.Boolean('财务报表')
    module_l10n_cn_dashboard = fields.Boolean('总账流程图')
    module_l10n_cn_voucher_auxiliary = fields.Boolean('凭证辅助核算')
    module_l10n_cn_voucher_arrange = fields.Boolean('凭证整理')
    module_l10n_cn_cashflow = fields.Boolean('现金流量')
    module_l10n_cn_carryover = fields.Boolean('期末结转')