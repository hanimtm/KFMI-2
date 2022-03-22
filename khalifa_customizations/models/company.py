# -*- coding: utf-8 -*-
from odoo import fields, models, api


class Company(models.Model):
    _inherit = 'res.company'

    default_supplier_id = fields.Many2one('res.partner', string='Default Supplier', domain=[('supplier_rank','>',0)])

    def set_default_supplier(self):
        # Set default supplier to any product that does not have any single supplier.
        product_ids = self.env['product.template'].search([('seller_ids','=',False)])
        for product_id in product_ids:
            product_id.write({
                'seller_ids': [(0,0,{'name':self.default_supplier_id.id})]
            })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
