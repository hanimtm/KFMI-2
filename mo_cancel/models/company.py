from odoo import api, fields, models
class ResCompany(models.Model):
    _inherit = "res.company"

    cancel_inventory_move_for_mo = fields.Boolean(string="Cancel Inventory Moves?")
    cancel_work_order_for_mo = fields.Boolean(string='Cancel Work Orders?')
