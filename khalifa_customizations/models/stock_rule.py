# -*- coding:utf-8 -*-
from odoo import fields, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    # def _get_matching_bom(self, product_id, company_id, values):
    #     res = super()._get_matching_bom(product_id, company_id, values)
    #     group_id = values.get('group_id')
    #     if group_id:
    #         return group_id.bom_id
    #     return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
