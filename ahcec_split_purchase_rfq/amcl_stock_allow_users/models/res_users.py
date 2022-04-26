# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResUser(models.Model):
    _inherit = 'res.users'

    allowed_users_warehouse = fields.Many2many('stock.warehouse', 'warehouse_user_rel', 'user_id', 'warehouse_id',
                                               string='Allowed Users for Warehouse')
    allowed_users_operation = fields.Many2many('stock.picking.type', 'picking_type_user_rel',
                                               'user_id', 'picking_type_id',
                                               string='Allowed Users for Operation')
