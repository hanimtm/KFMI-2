from odoo import models, fields


class WareHouseInherit(models.Model):
    _inherit = 'stock.warehouse'

    user_ids = fields.Many2many(comodel_name='res.users', string='User')


class StockPickingTypeInherit(models.Model):
    _inherit = 'stock.picking.type'

    user_ids = fields.Many2many(comodel_name='res.users', string='User')


class StockTypeInherit(models.Model):
    _inherit = 'stock.picking'

