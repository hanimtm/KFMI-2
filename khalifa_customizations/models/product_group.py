# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class ProductGroup(models.Model):
    _name = 'product.group'
    _description = 'Product Group'

    name = fields.Char(string='Brand')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('color_size', 'unique (name)',
         'The group must be unique per company !'),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
