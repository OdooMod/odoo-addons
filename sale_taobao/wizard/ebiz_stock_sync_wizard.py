# -*- coding: utf-8 -*- #

import time
from openerp.osv import osv, fields
import logging

_logger = logging.getLogger(__name__)
class ebiz_stock_sync_wizard(osv.osv_memory):
    _name = 'ebiz.stock.sync.wizard'    
 
    def ebiz_stock_sync_wizard(self, cr, uid, ids, context=None):
        active_ids = context.get('active_ids',[]);
        self.pool.get('ebiz.stock').sync_stock_qty(cr, uid, active_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}
 