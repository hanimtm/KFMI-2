# -*- coding: utf-8 -*-

from odoo import fields, models , api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    can_be_processed = fields.Boolean('Can Be Processed')
