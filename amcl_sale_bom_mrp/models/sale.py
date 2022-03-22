from odoo import api, models, fields, exceptions, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _action_launch_stock_rule(self):
        for line in self:
            super(SaleOrderLine, line.with_context(
                sale_line_id=line.id)
                  )._action_launch_stock_rule()
        return True
