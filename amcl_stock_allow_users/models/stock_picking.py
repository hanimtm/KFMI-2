# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    allowed_users = fields.Many2many('res.users', string='Allowed Users')

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        if self.picking_type_id:
            self.dummy_src_location = self.picking_type_id.default_location_src_id.id
            self.source_warehouse = self.picking_type_id.warehouse_id.id
        return {'domain': {
            'picking_type_id': [('warehouse_id.allowed_users', 'in', [self.env.user.id])]
        }}
