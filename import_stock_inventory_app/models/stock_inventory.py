# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo.tools.float_utils import float_compare, float_is_zero

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _change_standard_price(self, new_price):
        """Helper to create the stock valuation layers and the account moves
        after an update of standard price.

        :param new_price: new standard price
        """
        # Handle stock valuation layers.

        if self.filtered(lambda p: p.valuation == 'real_time') and not self.env['stock.valuation.layer'].check_access_rights('read', raise_exception=False):
            raise UserError(_("You cannot update the cost of a product in automated valuation as it leads to the creation of a journal entry, for which you don't have the access rights."))

        svl_vals_list = []
        company_id = self.env.company
        for product in self:
            if product.cost_method not in ('standard', 'average'):
                continue
            quantity_svl = product.sudo().quantity_svl
            if float_is_zero(quantity_svl, precision_rounding=product.uom_id.rounding):
                continue
            diff = new_price - product.standard_price
            value = company_id.currency_id.round(quantity_svl * diff)
            if company_id.currency_id.is_zero(value):
                continue

            svl_vals = {
                'company_id': company_id.id,
                'product_id': product.id,
                'description': _('Product value manually modified (from %s to %s)') % (product.standard_price, new_price),
                'value': value,
                'quantity': 0,
            }
            svl_vals_list.append(svl_vals)
        stock_valuation_layers = self.env['stock.valuation.layer'].sudo().create(svl_vals_list)

        if self._context.get('skip_valuation'):
            return True
        # Handle account moves.
        product_accounts = {product.id: product.product_tmpl_id.get_product_accounts() for product in self}
        am_vals_list = []
        for stock_valuation_layer in stock_valuation_layers:
            product = stock_valuation_layer.product_id
            value = stock_valuation_layer.value

            if product.type != 'product' or product.valuation != 'real_time':
                continue

            # Sanity check.
            if not product_accounts[product.id].get('expense'):
                raise UserError(_('You must set a counterpart account on your product category.'))
            if not product_accounts[product.id].get('stock_valuation'):
                raise UserError(_('You don\'t have any stock valuation account defined on your product category. You must define one before processing this operation.'))

            if value < 0:
                debit_account_id = product_accounts[product.id]['expense'].id
                credit_account_id = product_accounts[product.id]['stock_valuation'].id
            else:
                debit_account_id = product_accounts[product.id]['stock_valuation'].id
                credit_account_id = product_accounts[product.id]['expense'].id

            move_vals = {
                'journal_id': product_accounts[product.id]['stock_journal'].id,
                'company_id': company_id.id,
                'ref': product.default_code,
                'stock_valuation_layer_ids': [(6, None, [stock_valuation_layer.id])],
                'move_type': 'entry',
                'line_ids': [(0, 0, {
                    'name': _(
                        '%(user)s changed cost from %(previous)s to %(new_price)s - %(product)s',
                        user=self.env.user.name,
                        previous=product.standard_price,
                        new_price=new_price,
                        product=product.display_name
                    ),
                    'account_id': debit_account_id,
                    'debit': abs(value),
                    'credit': 0,
                    'product_id': product.id,
                }), (0, 0, {
                    'name': _(
                        '%(user)s changed cost from %(previous)s to %(new_price)s - %(product)s',
                        user=self.env.user.name,
                        previous=product.standard_price,
                        new_price=new_price,
                        product=product.display_name
                    ),
                    'account_id': credit_account_id,
                    'debit': 0,
                    'credit': abs(value),
                    'product_id': product.id,
                })],
            }
            am_vals_list.append(move_vals)

        account_moves = self.env['account.move'].sudo().create(am_vals_list)
        if account_moves:
            account_moves._post()


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    def _validate_accounting_entries(self):
        if self._context.get('skip_valuation'):
            return True
        am_vals = []
        for svl in self:
            if not svl.product_id.valuation == 'real_time':
                continue
            if svl.currency_id.is_zero(svl.value):
                continue
            am_vals += svl.stock_move_id._account_entry_move(svl.quantity, svl.description, svl.id, svl.value)
        if am_vals:
            account_moves = self.env['account.move'].sudo().create(am_vals)
            account_moves._post()
        for svl in self:
            # Eventually reconcile together the invoice and valuation accounting entries on the stock interim accounts
            if svl.company_id.anglo_saxon_accounting:
                svl.stock_move_id._get_related_invoices()._stock_account_anglo_saxon_reconcile_valuation(product=svl.product_id)
