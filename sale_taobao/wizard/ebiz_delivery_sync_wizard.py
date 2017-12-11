# -*- coding: utf-8 -*- #

import time
from openerp.osv import osv, fields
import logging

class ebiz_delivery_sync_wizard(osv.osv_memory):
    _name = 'ebiz.delivery.sync.wizard'

    def delivery_sync(self, cr, uid, ids, context=None):
        active_ids = context.get('active_ids', [ ])
        self.pool.get('ebiz.shop').orders_offline_send(cr, uid, [], active_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}


class ebiz_signed_sync_wizard(osv.osv_memory):
    _name = 'ebiz.signed.sync.wizard'

    def signed_sync(self, cr, uid, ids, context=None):
        active_ids = context.get('active_ids', [ ])
        self.pool.get('ebiz.shop').orders_signed(cr, uid, [], active_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

