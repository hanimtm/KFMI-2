# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    quantity_remaining = fields.Float('Quantity Remaining', compute='_quantity_remaining_compute',
                                      digits='Product Unit of Measure')

    @api.depends('quantity_done', 'product_uom_qty')
    def _quantity_remaining_compute(self):
        for data in self:
            data.quantity_remaining = data.product_uom_qty - data.quantity_done


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    mo_quantity = fields.Float('M/O Quantity', compute='_compute_mo_quantity')
    mo_name = fields.Many2one('mrp.production', 'MO', compute='_compute_mo_quantity')

    @api.depends('group_id')
    def _compute_mo_quantity(self):
        for picking in self:
            picking.mo_quantity = 0
            picking.mo_name = False
            if picking.group_id:
                mo = self.env['mrp.production'].search([(
                    'procurement_group_id', '=', picking.group_id.id
                )])
                if mo:
                    picking.mo_quantity = mo[0].product_qty
                    picking.mo_name = mo[0].id
