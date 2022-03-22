# -*- coding : utf-8 -*-

from odoo import models, fields, api


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values,
                         bom):
        context = self.env.context

        bom_new = self.env['sale.order.line'].search([('id', '=', context.get('sale_line_id'))]).bom_id
        if bom_new:
            res = super(StockRule, self)._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name,
                                                          origin,
                                                          company_id, values, bom_new)
        else:
            res = super(StockRule, self)._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin,
                                                      company_id, values, bom)
        return res
