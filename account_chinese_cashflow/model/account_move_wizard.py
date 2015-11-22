# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import tools
from datetime import datetime

class account_move_wizard(osv.osv_memory):
    _name = "account.move.wizard"
    _description = "Create account entry"
    _columns = {
        'force_posted': fields.boolean('更新已记账凭证'),
        'period_id':fields.many2one('account.period','会计期间'),
        'update_method': fields.selection([('noset','部分，仅未设置'),('update','全部，重算已设置')],'更新范围')
   }
    _defaults = {'update_method':'noset'
    }

    def default_get(self, cr, uid, fields, context):
        """ To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        res = super(account_move_wizard, self).default_get(cr, uid, fields, context=context)
        period_id = self.pool.get('account.period').find(cr, uid,  datetime.now(), context=context)[0]
        res['period_id'] = period_id

        try:
            model, journal_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock_account', 'stock_journal')
            res['journal_id'] = journal_id
        except (orm.except_orm, ValueError):
            pass
        return res

    def button_wizard(self, cr, uid, ids, context=None):
        wiz = self.browse(cr, uid, ids[0])
        aml = self.pool.get('account.move.line')
        for am_id in context['active_ids']:
            if wiz.force_posted == 1:
                aml_domain = [('move_id.id','=','%s'%am_id)]
            else:
                aml_domain = [('move_id.id','=','%s'%am_id),('state','!=','posted')]
            #if wiz.peroid_id is not None:
            #    aml_domain.append(('period_id','=','%s'%wiz.peroid_id))
            aml_list = aml.search(cr,uid,aml_domain)
            aml_objs = aml.browse(cr, uid, aml_list, context=context)
            cash_flag = 0
            for aml_obj in aml_objs:
                if aml_obj.account_id.type == 'liquidity':
                    cash_flag = 1
            if cash_flag == 1:
                for aml_obj in aml_objs:
                    account_category = aml_obj.account_id.category_id
                    if (account_category.id != 0 and (aml_obj.av_cat_id.id == 0 or wiz.update_method=='noset')):
                        #aml.av_cat_id = account_category
                        aml_obj.write({'av_cat_id':account_category.id})
            #x = aml;
        return {}

    def button_clear(self, cr, uid, ids, context=None):
        aml = self.pool.get('account.move.line')
        for am_id in context['active_ids']:
            aml_domain = [('move_id.id','=','%s'%am_id)]
            aml_list = aml.search(cr,uid,aml_domain)
            aml_objs = aml.browse(cr, uid, aml_list, context=context)
            for aml_obj in aml_objs:
                aml_obj.write({'av_cat_id':None})
            #x = aml;
        return {}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
