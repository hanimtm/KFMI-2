# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.branch_id)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.branch_id,
                                states={'purchase': [('readonly', True)],
                                        'done': [('readonly', True)],
                                        'cancel': [('readonly', True)]})

    @api.model
    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        res.update({'branch_id': self.branch_id.id})
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    branch_id = fields.Many2one('company.branch', related='order_id.branch_id', string="Branch",
                                store=True, readonly=True)

    def _prepare_stock_moves(self, picking):
        self.ensure_one()
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        if res and res[0]:
            res[0].update({'branch_id': self.branch_id.id})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
