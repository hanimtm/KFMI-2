# -*- coding:utf-8 -*-
from odoo.tools import float_compare
from odoo import fields, models, api


class Sale(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id')
    def compute_bom_cost(self):
        """
        Compute BOM Cost
        :return:
        """
        print ('Compute BOM Cost ... ')
        for order_line in self:
            if order_line.product_id:
                bom = self.env['mrp.bom']._bom_find(order_line.product_id)[order_line.product_id]
                if bom:
                    order_line.bom_cost = order_line.product_id._compute_bom_price(bom,)
                else:
                    bom = self.env['mrp.bom'].search(
                        [('byproduct_ids.product_id', '=', order_line.product_id.id)],
                        order='sequence, product_id, id', limit=1)
                    if bom:
                        price = order_line.product_id._compute_bom_price(bom, byproduct_bom=True)
                        if price:
                            order_line.bom_cost = price

    bom_id = fields.Many2one('mrp.bom', string='BOM', copy=False)
    label = fields.Char(string='Label', copy=False)
    drawing = fields.Char(string='Drawing', copy=False)
    sec_wh_id = fields.Many2one('sec.wh', string='SEC WH')
    line_no = fields.Char(string="Line No")
    non_standard_bom = fields.Boolean(related='product_id.non_standard_bom', string='Non Standard BOM')
    bom_cost = fields.Float('BOM Cost', compute=compute_bom_cost)

    @api.onchange('product_id')
    def onchange_product_set_bom(self):
        if self.product_id.standard_bom:
            bom = self.env['mrp.bom']._bom_find(self.product_id, company_id=self.company_id.id, bom_type='normal')[self.product_id]
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
