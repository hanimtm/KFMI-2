# -*- coding: utf-8 -*-

from odoo import fields, models
import logging
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    def change_policy(self):
        for product in self:
            if product.invoice_policy == 'order':
                product.write({'invoice_policy': 'delivery'})
            elif product.invoice_policy == 'delivery':
                product.write({'invoice_policy': 'order'})
            else:
                raise ValidationError("WARNING: There is one or multi product hasn't invoice policy")

