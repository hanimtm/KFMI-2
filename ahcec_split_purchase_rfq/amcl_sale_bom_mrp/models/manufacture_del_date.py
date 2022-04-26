# -*- coding : utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api
from datetime import datetime


# class MRPProductionInherit(models.Model):
#     _inherit = "mrp.production"
#
#     product_description = fields.Char(string="Description")
#
#     @api.onchange('product_id')
#     def onchange_product_description(self):
#         self.product_description = self.product_id.description_sale
#
#
# class MRPWorkOrderInherit(models.Model):
#     _inherit = "mrp.workorder"
#
#     product_description = fields.Char(string="Description", related="production_id.product_description", store=True)

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom):
        print(values)
        res = super(StockRule, self)._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom)
        if values.get('move_dest_ids'):
            move_dest_ids = values.get('move_dest_ids')[0]
            for move in move_dest_ids:
                if move:
                    res.update({
                        'bom_id': move.sale_line_id.bom_id.id,
                    })
        return res

    # def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
    #     res = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id,
    #                                                        name, origin, values, group_id)
    #     res['product_description'] = product_id.product_tmpl_id.description_sale
    #     return res