# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, SUPERUSER_ID
from . import models,report

def post_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['account.journal'].init()
    env['account.account'].init()