# -*- coding: utf-8 -*-
from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # This will be a json field to store origin detail of the each line in purchase order
    source_detail = fields.Char(string='Source Detail')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
