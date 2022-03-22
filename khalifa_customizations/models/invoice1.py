# -*- coding:utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang, format_date, get_lang
from collections import defaultdict
import json


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_default_tax_id(self):
        if self.move_type in ('out_invoice', 'out_refund'):
            return self.env.company.account_sale_tax_id or False
        else:
            return self.env.company.account_purchase_tax_id or False

    discount_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')], string='Discount Type',
                                     readonly=True, states={'draft': [('readonly', False)]}, default='percent')
    discount_rate = fields.Float('Discount Amount', digits=(16, 2), readonly=True,
                                 states={'draft': [('readonly', False)]})
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, tracking=True,
                                      compute='_compute_amount')
    discount_tax = fields.Many2one('account.tax', string='Discount Tax',
                                   default=_get_default_tax_id)
    global_discount_tax = fields.Monetary(string='Discount Tax amount', store=True, readonly=True, tracking=True,
                                          compute='_compute_discount_tax')

    @api.depends('invoice_line_ids', 'amount_untaxed', 'amount_tax', 'amount_discount', 'discount_type',
                 'discount_rate')
    def _compute_all_price(self):
        price_before_discount = discount = 0
        for line in self.invoice_line_ids:
            price_before_discount += line.price_before_discount
            discount += line.discount_amount

        self.price_before_discount = price_before_discount
        self.discount = discount + self.amount_discount

    @api.depends('discount_rate', 'discount_tax', 'amount_discount')
    def _compute_discount_tax(self):
        for move in self:
            move.global_discount_tax = 0
            if move.discount_tax and move.amount_discount > 0:
                move.global_discount_tax = (move.amount_discount * move.discount_tax.amount) / 100

    @api.depends('line_ids.amount_currency', 'line_ids.tax_base_amount', 'line_ids.tax_line_id', 'partner_id',
                 'currency_id', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        for move in self:
            if not move.is_invoice(include_receipts=True):
                move.tax_totals_json = None
                continue
            tax_lines_data = move._prepare_tax_lines_data_for_totals_from_invoice()
            if move.global_discount_tax > 0:
                move.tax_totals_json = json.dumps({
                    **self._get_tax_totals_new(move.partner_id, tax_lines_data, move.amount_total, move.amount_untaxed,
                                           move.currency_id,move.amount_discount,move.global_discount_tax),
                    'allow_tax_edition': move.is_purchase_document(include_receipts=False) and move.state == 'draft',
                })
            else:
                move.tax_totals_json = json.dumps({
                    **self._get_tax_totals(move.partner_id, tax_lines_data, move.amount_total, move.amount_untaxed,
                                           move.currency_id),
                    'allow_tax_edition': move.is_purchase_document(include_receipts=False) and move.state == 'draft',
                })

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_amount(self):
        for move in self:

            if move.payment_state == 'invoicing_legacy':
                move.payment_state = move.payment_state
                continue

            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_to_pay = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = set()

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_to_pay += line.balance
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.move_type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            print('Total  ::', total + move.global_discount_tax + move.amount_discount)
            print('Total 21::', total_currency + move.global_discount_tax + move.amount_discount)

            if move.move_type in ('out_invoice','out_refund'):
                total_untaxed = total_untaxed - move.discount
                total_untaxed_currency = total_untaxed_currency + move.discount
                total_tax = total_tax + move.global_discount_tax
                total_tax_currency = total_tax_currency + move.global_discount_tax
                total_currency = total_currency + move.global_discount_tax + move.amount_discount

            else:
                total_untaxed = total_untaxed - move.discount
                total_untaxed_currency = total_untaxed_currency - move.discount

            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
            move.amount_residual_signed = total_residual

            currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id

            new_pmt_state = 'not_paid' if move.move_type != 'entry' else False

            if move.is_invoice(include_receipts=True) and move.state == 'posted':

                if currency.is_zero(move.amount_residual):
                    if all(payment.is_matched for payment in move._get_reconciled_payments()):
                        new_pmt_state = 'paid'
                    else:
                        new_pmt_state = move._get_invoice_in_payment_state()
                elif currency.compare_amounts(total_to_pay, total_residual) != 0:
                    new_pmt_state = 'partial'

            if new_pmt_state == 'paid' and move.move_type in ('in_invoice', 'out_invoice', 'entry'):
                reverse_type = move.move_type == 'in_invoice' and 'in_refund' or move.move_type == 'out_invoice' and 'out_refund' or 'entry'
                reverse_moves = self.env['account.move'].search(
                    [('reversed_entry_id', '=', move.id), ('state', '=', 'posted'), ('move_type', '=', reverse_type)])

                reverse_moves_full_recs = reverse_moves.mapped('line_ids.full_reconcile_id')
                if reverse_moves_full_recs.mapped('reconciled_line_ids.move_id').filtered(lambda x: x not in (
                        reverse_moves + reverse_moves_full_recs.mapped('exchange_move_id'))) == move:
                    new_pmt_state = 'reversed'
            move.payment_state = new_pmt_state

    @api.onchange('discount_type')
    def _onchange_discount_type(self):
        if not self.discount_tax:
            self.discount_tax = self.env.company.account_sale_tax_id.id or False

    @api.onchange('discount_type', 'discount_rate', 'invoice_line_ids', 'amount_discount','discount_tax')
    def supply_rate(self):
        for inv in self:
            if inv.discount_type == 'amount':
                if inv.discount_tax:
                    discount = inv.discount_rate
                else:
                    discount = inv.discount_rate
                inv.update({
                    'discount': inv.discount + discount,
                    'amount_discount':discount})

            elif inv.discount_type == 'percentage':
                if inv.discount_tax:
                    discount = inv.price_before_discount * ((inv.discount_rate or 0.0) / 100.0)
                else:
                    discount = inv.price_before_discount * ((inv.discount_rate or 0.0) / 100.0)
                print(discount)
                inv.update({
                    'discount': inv.discount + discount,
                    'amount_discount':discount})
            else:
                discount = 0
                inv.update({
                    'discount': discount,
                    'amount_discount':discount
                })
            inv._compute_tax_totals_json()

    def button_dummy(self):
        self.supply_rate()
        return True

    @api.model
    def _get_tax_totals_new(self, partner, tax_lines_data, amount_total, amount_untaxed, currency, global_discount,global_discount_tax):
        lang_env = self.with_context(lang=partner.lang).env
        account_tax = self.env['account.tax']

        grouped_taxes = defaultdict(
            lambda: defaultdict(lambda: {'base_amount': 0.0, 'tax_amount': 0.0, 'base_line_keys': set()}))
        subtotal_priorities = {}
        for line_data in tax_lines_data:
            tax_group = line_data['tax'].tax_group_id

            if tax_group.preceding_subtotal:
                subtotal_title = tax_group.preceding_subtotal
                new_priority = tax_group.sequence
            else:
                subtotal_title = _("Untaxed Amount")
                new_priority = 0

            if subtotal_title not in subtotal_priorities or new_priority < subtotal_priorities[subtotal_title]:
                subtotal_priorities[subtotal_title] = new_priority

            tax_group_vals = grouped_taxes[subtotal_title][tax_group]

            if 'base_amount' in line_data:
                # Base line
                if tax_group == line_data.get('tax_affecting_base', account_tax).tax_group_id:
                    continue

                if line_data['line_key'] not in tax_group_vals['base_line_keys']:
                    tax_group_vals['base_line_keys'].add(line_data['line_key'])
                    tax_group_vals['base_amount'] += line_data['base_amount']

            else:
                tax_group_vals['tax_amount'] += line_data['tax_amount']

        groups_by_subtotal = {}
        for subtotal_title, groups in grouped_taxes.items():
            groups_vals = [{
                'tax_group_name': group.name,
                'tax_group_amount': amounts['tax_amount'] - global_discount_tax,
                'tax_group_base_amount': amounts['base_amount'],
                'formatted_tax_group_amount': formatLang(lang_env, amounts['tax_amount'] - global_discount_tax,
                                                         currency_obj=currency),
                'formatted_tax_group_base_amount': formatLang(lang_env, amounts['base_amount'], currency_obj=currency),
                'tax_group_id': group.id,
                'group_key': '%s-%s' % (subtotal_title, group.id),
            } for group, amounts in sorted(groups.items(), key=lambda l: l[0].sequence)]

            groups_by_subtotal[subtotal_title] = groups_vals

        subtotals_list = []  # List, so that we preserve their order
        previous_subtotals_tax_amount = 0
        for subtotal_title in sorted((sub for sub in subtotal_priorities), key=lambda x: subtotal_priorities[x]):
            subtotal_value = amount_untaxed + previous_subtotals_tax_amount
            subtotals_list.append({
                'name': subtotal_title,
                'amount': subtotal_value,
                'formatted_amount': formatLang(lang_env, subtotal_value, currency_obj=currency),
            })

            subtotal_tax_amount = sum(group_val['tax_group_amount'] for group_val in groups_by_subtotal[subtotal_title])
            previous_subtotals_tax_amount += subtotal_tax_amount

        return {
            'amount_total': amount_total,
            'amount_untaxed': amount_untaxed,
            'formatted_amount_total': formatLang(lang_env, amount_total, currency_obj=currency),
            'formatted_amount_untaxed': formatLang(lang_env, amount_untaxed, currency_obj=currency),
            'groups_by_subtotal': groups_by_subtotal,
            'subtotals': subtotals_list,
            'allow_tax_edition': False,
        }


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    discount = fields.Float(string='Discount (%)', digits=(16, 20), default=0.0)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
