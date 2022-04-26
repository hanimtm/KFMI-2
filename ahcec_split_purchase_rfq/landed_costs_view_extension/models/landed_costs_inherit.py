from odoo import models, fields


class LandedCostsInherit(models.Model):
    _inherit = 'stock.landed.cost'

    vendor_id = fields.Many2one(related='vendor_bill_id.partner_id')
