from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    produce_percentage = fields.Float('Percentage(%)')

    @api.onchange('produce_percentage', 'product_uom_qty')
    def onchange_qty_percentage(self):
        """
        :return:
        """
        total_qty = self.production_id.product_qty
        if self._context.get('update_percentage'):
            if total_qty and self.produce_percentage:
                self.product_uom_qty = (total_qty * self.produce_percentage) / 100
                self.cost_share = self.produce_percentage
        if self._context.get('update_qty'):
            if total_qty and self.product_uom_qty:
                self.produce_percentage = (100 * self.product_uom_qty) / total_qty
                self.cost_share = self.produce_percentage
