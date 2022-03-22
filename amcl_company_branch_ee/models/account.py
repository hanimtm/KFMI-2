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
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.branch_id,
                                readonly=True, states={'draft': [('readonly', False)]})

    @api.onchange('state', 'partner_id', 'invoice_line_ids')
    def _onchange_allowed_purchase_ids(self):
        """
        The purpose of the method is to define a domain for the available
        purchase orders.
        """
        result = {}
        # A PO can be selected only if at least one PO line is not already in the invoice
        purchase_line_ids = self.invoice_line_ids.mapped('purchase_line_id')
        purchase_ids = self.invoice_line_ids.mapped('purchase_id').filtered(lambda r: r.order_line <= purchase_line_ids)
        result['domain'] = {'purchase_id': [
            ('invoice_status', '=', 'to invoice'),
            ('partner_id', 'child_of', self.partner_id.id),
            ('id', 'not in', purchase_ids.ids),
            ('branch_id', '=', self.branch_id.id)
        ]}
        return result

    @api.model
    def _get_refund_copy_fields(self):
        copy_fields = ['company_id', 'user_id', 'fiscal_position_id', 'branch_id']
        return self._get_refund_common_fields() + self._get_refund_prepare_fields() + copy_fields

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id
        self.branch_id = self.purchase_id.branch_id.id

        new_lines = self.env['account.move.line']
        for line in self.purchase_id.order_line - self.invoice_line_ids.mapped('purchase_line_id'):
            data = self._prepare_invoice_line_from_po_line(line)
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line

        self.invoice_line_ids += new_lines
        self.payment_term_id = self.purchase_id.payment_term_id
        self.env.context = dict(self.env.context, from_purchase_order_change=True)
        self.purchase_id = False
        return {}


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    branch_id = fields.Many2one('company.branch', string="Branch", related='move_id.branch_id', store=True,
                                readonly=True)
    purchase_id = fields.Many2one('purchase.order', string="Purchase Order", store=True,
                                  related='purchase_line_id.order_id')


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    branch_id = fields.Many2one('company.branch', string="Branch", default=lambda self: self.env.user.branch_id)

    def action_validate_invoice_payment(self):
        if any(len(record.invoice_ids) != 1 for record in self):
            # For multiple invoices, there is account.register.payments wizard
            raise UserError(_("This method should only be called to process a single invoice's payment."))
        self.branch_id = self.invoice_ids[0].branch_id.id
        return self.post()


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.payment.register"

    def _create_payment_vals_from_batch(self, batch_result):
        res = super(AccountRegisterPayments, self)._create_payment_vals_from_batch(batch_result)
        if self.env.context.get('active_model') == 'account.move' and self.env.context.get('active_ids'):
            move_ids = self.env['account.move'].search([('id', 'in', self.env.context.get('active_ids'))])
            check_branch_diff = set([x.branch_id.id for x in move_ids])
            if len(check_branch_diff) > 1:
                raise UserError(_("Cannot create payment for different branches."))
            elif len(check_branch_diff) == 1:
                res['branch_id'] = move_ids.mapped('branch_id').ids[0]
        return res

    def _create_payment_vals_from_wizard(self):
        res = super(AccountRegisterPayments, self)._create_payment_vals_from_wizard()
        if self.env.context.get('active_model') == 'account.move' and self.env.context.get('active_ids'):
            move_ids = self.env['account.move'].search([('id', 'in', self.env.context.get('active_ids'))])
            check_branch_diff = set([x.branch_id.id for x in move_ids])
            if len(check_branch_diff) > 1:
                raise UserError(_("Cannot create payment for different branches."))
            elif len(check_branch_diff) == 1:
                res['branch_id'] = move_ids.mapped('branch_id').ids[0]
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
