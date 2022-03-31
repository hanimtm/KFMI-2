# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.osv import expression
from odoo.exceptions import UserError

class Product(models.Model):
    _inherit = 'product.template'

    @api.onchange('list_price')
    def onchange_list_price(self):
        if self.list_price <= self.standard_price:
            self.write({'list_price': self.standard_price})
            raise UserError(_('You can not enter a Sale Price less than the Cost price.'))
