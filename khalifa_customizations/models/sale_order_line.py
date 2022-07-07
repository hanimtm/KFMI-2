# -*- coding:utf-8 -*-
from odoo.tools import float_compare
from odoo import fields, models, api
from odoo.tools import float_round


class Sale(models.Model):
    _inherit = 'sale.order.line'

    def _get_operation_line(self, product, bom, qty):
        operations = []
        total = 0.0
        qty = bom.product_uom_id._compute_quantity(qty, bom.product_tmpl_id.uom_id)
        for operation in bom.operation_ids:
            if operation._skip_operation_line(product):
                continue
            operation_cycle = float_round(qty / operation.workcenter_id.capacity, precision_rounding=1, rounding_method='UP')
            duration_expected = operation_cycle * (operation.time_cycle + (operation.workcenter_id.time_stop + operation.workcenter_id.time_start))
            total = ((duration_expected / 60.0) * operation.workcenter_id.costs_hour)
            operations.append({
                'operation': operation,
                'duration_expected': duration_expected,
                'total': self.env.company.currency_id.round(total),
            })
        return operations

    def _get_price(self, bom, factor, product):
        price = 0
        if bom.operation_ids:
            operation_cycle = float_round(factor, precision_rounding=1, rounding_method='UP')
            operations = self._get_operation_line(product, bom, operation_cycle)
            price += sum([op['total'] for op in operations])

        for line in bom.bom_line_ids:
            if line._skip_bom_line(product):
                continue
            if line.child_bom_id:
                qty = line.product_uom_id._compute_quantity(line.product_qty * (factor / bom.product_qty) , line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_price = self._get_price(line.child_bom_id, qty, line.product_id)
                byproduct_cost_share = sum(line.child_bom_id.byproduct_ids.mapped('cost_share'))
                if byproduct_cost_share:
                    sub_price *= float_round(1 - byproduct_cost_share / 100, precision_rounding=0.0001)
                price += sub_price
            else:
                prod_qty = line.product_qty * factor / bom.product_qty
                company = bom.company_id or self.env.company
                not_rounded_price = line.product_id.uom_id._compute_price(line.product_id.with_context(force_comany=company.id).standard_price, line.product_uom_id) * prod_qty
                price += company.currency_id.round(not_rounded_price)
        return price

    def _get_bom_lines(self, bom, bom_quantity, product):
        total = 0
        for line in bom.bom_line_ids:
            line_quantity = (bom_quantity / (bom.product_qty or 1.0)) * line.product_qty
            if line._skip_bom_line(product):
                continue
            company = bom.company_id or self.env.company
            price = line.product_id.uom_id._compute_price(line.product_id.with_company(company).standard_price, line.product_uom_id) * line_quantity
            if line.child_bom_id:
                factor = line.product_uom_id._compute_quantity(line_quantity, line.child_bom_id.product_uom_id)
                sub_total = self._get_price(line.child_bom_id, factor, line.product_id)
                byproduct_cost_share = sum(line.child_bom_id.byproduct_ids.mapped('cost_share'))
                if byproduct_cost_share:
                    sub_total *= float_round(1 - byproduct_cost_share / 100, precision_rounding=0.0001)
            else:
                sub_total = price
            sub_total = self.env.company.currency_id.round(sub_total)
            total += sub_total
        return total

    def _get_byproducts_lines(self, bom):
        byproduct_cost_portion = 0
        for byproduct in bom.byproduct_ids:
            cost_share = byproduct.cost_share / 100
            byproduct_cost_portion += cost_share
        return byproduct_cost_portion

    @api.depends('product_id','bom_id','order_id')
    def compute_bom_cost(self):
        """
        Compute BOM Cost
        :return:
        """
        for order_line in self:
            bom_cost = 0
            if order_line.bom_id:
                bom = order_line.bom_id
            else:
                bom = self.env['mrp.bom']._bom_find(order_line.product_id)[order_line.product_id]
            if bom:
                operations = self._get_operation_line(order_line.product_id, bom, float_round(
                    1, precision_rounding=1,  rounding_method='UP'))
                bom_cost = sum([op['total'] for op in operations])
                bom_cost += self._get_bom_lines(bom, 1, order_line.product_id)
            else:
                bom = self.env['mrp.bom'].search(
                            [('byproduct_ids.product_id', '=', order_line.product_id.id)],
                            order='sequence, product_id, id', limit=1)
                if bom:
                    operations = self._get_operation_line(order_line.product_id, bom, float_round(
                        1, precision_rounding=1, rounding_method='UP'))
                    bom_cost = sum([op['total'] for op in operations])
                    bom_cost += self._get_bom_lines(bom, 1, order_line.product_id)
            byproduct_cost_portion = self._get_byproducts_lines(bom)
            cost_share = float_round(1 - byproduct_cost_portion, precision_rounding=0.0001)
            bom_cost = bom_cost * cost_share
            order_line.bom_cost = bom_cost

    bom_id = fields.Many2one('mrp.bom', string='BOM', copy=False)
    label = fields.Char(string='Label', copy=False)
    drawing = fields.Char(string='Drawing', copy=False)
    sec_wh_id = fields.Many2one('sec.wh', string='SEC WH')
    line_no = fields.Char(string="Line No")
    non_standard_bom = fields.Boolean(related='product_id.non_standard_bom', string='Non Standard BOM')
    bom_cost = fields.Float('BOM Cost', compute='compute_bom_cost')

    @api.onchange('product_id')
    def onchange_product_set_bom(self):
        if self.product_id.standard_bom:
            bom = self.env['mrp.bom']._bom_find(self.product_id, company_id=self.company_id.id, bom_type='normal')[
                self.product_id]
            if bom:
                self.bom_id = bom.id

    # def _prepare_procurement_group_vals(self):
    #     res = super()._prepare_procurement_group_vals()
    #     if self.bom_id:
    #         res.update({
    #             'bom_id':self.bom_id.id
    #         })
    #     return res

    # def _action_launch_stock_rule(self, previous_product_uom_qty=False):
    #     """
    #     Launch procurement group run method with required/custom fields genrated by a
    #     sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
    #     depending on the sale order line product rule.
    #     """
    #     precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #     procurements = []
    #     for line in self:
    #         line = line.with_company(line.company_id)
    #         if line.state != 'sale' or not line.product_id.type in ('consu','product'):
    #             continue
    #         qty = line._get_qty_procurement(previous_product_uom_qty)
    #         if float_compare(qty, line.product_uom_qty, precision_digits=precision) == 0:
    #             continue

    #         group_id = line._get_procurement_group()
    #         if not group_id:
    #             group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
    #             line.order_id.procurement_group_id = group_id
    #         else:
    #             # In case the procurement group is already created and the order was
    #             # cancelled, we need to update certain values of the group.
    #             updated_vals = {}
    #             if group_id.partner_id != line.order_id.partner_shipping_id:
    #                 updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
    #             if group_id.move_type != line.order_id.picking_policy:
    #                 updated_vals.update({'move_type': line.order_id.picking_policy})
    #             # if line.bom_id:
    #             #     updated_vals.update({
    #             #         'bom_id': line.bom_id.id
    #             #         })
    #             if updated_vals:
    #                 group_id.write(updated_vals)
    #         values = line._prepare_procurement_values(group_id=group_id)
    #         product_qty = line.product_uom_qty - qty

    #         line_uom = line.product_uom
    #         quant_uom = line.product_id.uom_id
    #         product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
    #         procurements.append(self.env['procurement.group'].Procurement(
    #             line.product_id, product_qty, procurement_uom,
    #             line.order_id.partner_shipping_id.property_stock_customer,
    #             line.name, line.order_id.name, line.order_id.company_id, values))
    #     if procurements:
    #         self.env['procurement.group'].run(procurements)

    #     # This next block is currently needed only because the scheduler trigger is done by picking confirmation rather than stock.move confirmation
    #     orders = self.mapped('order_id')
    #     for order in orders:
    #         pickings_to_confirm = order.picking_ids.filtered(lambda p: p.state not in ['cancel', 'done'])
    #         if pickings_to_confirm:
    #             # Trigger the Scheduler for Pickings
    #             pickings_to_confirm.action_confirm()
    #     return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
