# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv

class account_account(osv.Model):
    _inherit = 'account.account'
    _columns = {'category_id':
        fields.many2one('account.voucher.category','Category')}

    def button_cashflow(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for move in self.browse(cr, uid, ids, context=context):
            aml_domain = [('move_id.id','=','%s'%move.id)]
            aml = self.pool.get('account.move.line')
            aml_list = aml.search(cr,uid,aml_domain)
            aml_objs = aml.browse(cr, uid, aml_list, context=context)
            for aml in aml_objs:
                account_category = aml.account_id.category_id
                if (account_category.id != False and aml.av_cat_id.id == False):
                    #aml.av_cat_id = account_category
                    aml.write({'av_cat_id':account_category.id})
            #x = aml;
        return {}

class scrvw_report_account_voucher_category(osv.Model):
    _inherit = 'scrvw.report.account.voucher.category'
    def init(self, cr):
        query = """
            CREATE OR REPLACE VIEW %s AS (
                SELECT aml.id, aml.name, aml.debit, aml.credit,
                       aml.av_cat_id AS avc_id, avc.code AS avc_code,
                       avc.name AS avc_name,
                       avc.parent_id AS avc_parent_id,
                       avcp.code AS avc_parent_code,
                       avcp.name AS avc_parent_name,
                       avcp.parent_id AS avc_grand_parent_id,
                       avcgp.code AS avc_grand_parent_code,
                       avcgp.name AS avc_grand_parent_name,
                       aml.analytic_account_id AS aa_id,
                       aml.account_id, aml.date,
                       EXTRACT(MONTH FROM date) AS month,
                       aml.period_id, (aml.debit-aml.credit) AS balance
                FROM account_move_line AS aml
                INNER JOIN account_account AS aa ON aml.account_id=aa.id
                INNER JOIN account_voucher_category AS avc
                      ON aml.av_cat_id=avc.id
                INNER JOIN account_voucher_category AS avcp
                      ON avcp.id=avc.parent_id
                LEFT JOIN account_voucher_category AS avcgp
                      ON avcgp.id=avcp.parent_id
                --WHERE aa.type = 'liquidity'
            )""" % (self._name.replace('.', '_'))
        cr.execute(query)