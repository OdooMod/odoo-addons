# -*- coding: utf-8 -*-
##############################################################################
# Author: waveyeung<waveyeung@gmail.com>
#         http://github.com/waveyeung
##############################################################################

from openerp import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def __init__(self,pool,cr):
        su = super(PurchaseOrder, self)
        if len(su.STATE_SELECTION) == 9:
            su.STATE_SELECTION.insert(4,('approve1','Purchase Confirmed'))
        su.__init__(pool,cr)

    def wkf_approve_order(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approved'})
        return True