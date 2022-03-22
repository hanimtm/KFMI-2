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

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    branch_id = fields.Many2one('company.branch', string="Branch",
                                readonly=True, states={'draft': [('readonly', False)],
                                                       'sent': [('readonly', False)]})

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        if self.warehouse_id.company_id:
            self.company_id = self.warehouse_id.company_id.id
        if self.warehouse_id:
            if not self.warehouse_id.branch_id:
                raise ValidationError(_('Please select branch in %s Warehouse.' % (self.warehouse_id.name)))
            else:
                self.branch_id = self.warehouse_id.branch_id.id

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if not order.warehouse_id.branch_id:
                raise ValidationError(_('Please select branch in %s Warehouse.' % (order.warehouse_id.name)))
            elif order.warehouse_id.branch_id.id != order.branch_id.id:
                raise ValidationError(_('Please select branch as per warehouse branch.'))
        return res

    def _prepare_invoice(self):
        self.ensure_one()
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({'branch_id': self.branch_id.id})
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    branch_id = fields.Many2one(related='order_id.branch_id', string='Branch', store=True, readonly=True)

    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        res.update({'branch_id': self.branch_id.id})
        return res


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        if res and order:
            res.write({'branch_id': order.branch_id.id})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
