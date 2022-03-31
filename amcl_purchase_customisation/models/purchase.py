 # -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError, ValidationError
from itertools import groupby


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_create_invoice(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoice_vals_list = []
        moves = self.env['account.move']
        for order in self:
            if order.invoice_status != 'to invoice':
                continue
            order = order.with_company(order.company_id)
            grouped_po_lines = groupby(order.order_line.sorted('billing_document'), key=lambda l: l.billing_document)
            for product, po_lines in grouped_po_lines:
                invoice_vals_list = []
                invoice_vals = order._prepare_invoice()
                dat = False
                document = False
                for line in po_lines:
                    invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_account_move_line()))
                    invoice_vals['ref'] = line.billing_document
                    invoice_vals['branch_id'] = order.branch_id.id
                    invoice_vals_list.append(invoice_vals)
                    dat = line.bill_date
                    document = line.billing_document
                AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
                for vals in invoice_vals_list:
                    if not self.env['account.move'].search([('ref','=',document)]):
                        print(vals)
                        invoice = AccountMove.with_company(vals['company_id']).create(vals)
                        invoice.write({'invoice_date': dat})
                        moves |= invoice

            moves.filtered(
                lambda m: m.currency_id.round(m.amount_total) < 0).action_switch_invoice_into_refund_credit_note()
            return self.action_view_invoice(moves)
