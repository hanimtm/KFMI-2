from odoo import fields, models , api, _


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    allowed_users = fields.Many2many('res.users', 'picking_type_user_rel', 'picking_type_id', 'user_id', string='Allowed Users')
