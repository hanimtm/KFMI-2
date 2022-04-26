# -*- coding: utf-8 -*-

from odoo import fields, models , api, _


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    allowed_users = fields.Many2many('res.users', 'warehouse_user_rel', 'warehouse_id', 'user_id',  string='Allowed Users')
