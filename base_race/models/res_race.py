# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomk.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResRace(models.Model):
    _name = 'res.race'

    code = fields.Char(string='代码')
    name = fields.Char(string='名称')


