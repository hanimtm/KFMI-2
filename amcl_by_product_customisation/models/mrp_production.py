from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'mrp.production'

    def action_confirm(self):

        for production in self:
            if self.move_byproduct_ids:
                move_byproduct_qty = []
                [move_byproduct_qty.append(by_product.product_uom_qty) for by_product in self.move_byproduct_ids]
                if production.product_qty != sum(move_byproduct_qty):
                    raise ValidationError(_('Total Production Quantity and sum of byproduct Quantity should be same.'))
        res = super(StockMove, self).action_confirm()
        return res

    @api.onchange('bom_id', 'product_qty', 'product_uom_id')
    def _onchange_move_finished(self):
        """
        :return:
        """
        res = super(StockMove, self)._onchange_move_finished()
        for by_product_line in self.move_byproduct_ids:
            if by_product_line.produce_percentage:
                by_product_line.product_uom_qty = (self.product_qty * by_product_line.produce_percentage) / 100
            else:
                by_product_line.produce_percentage = 0
                by_product_line.product_uom_qty = 0
        return res
