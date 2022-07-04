# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def button_create_landed_costs(self):
        self.ensure_one()
        landed_costs_lines = self.line_ids.filtered(lambda line: line.is_landed_costs_line)

        landed_costs = self.env['stock.landed.cost'].create({
            'vendor_bill_id': self.id,
            'cost_lines': [(0, 0, {
                'product_id': l.product_id.id,
                'name': l.product_id.name,
                'account_id': l.product_id.product_tmpl_id.get_product_accounts()['stock_input'].id or l.product_id.property_account_income_id.id,
                'price_unit': l.currency_id._convert(l.price_subtotal, l.company_currency_id, l.company_id,
                                                     l.move_id.date),
                'split_method': l.product_id.split_method_landed_cost or 'equal',
            }) for l in landed_costs_lines],
        })
        action = self.env["ir.actions.actions"]._for_xml_id("stock_landed_costs.action_stock_landed_cost")
        return dict(action, view_mode='form', res_id=landed_costs.id, views=[(False, 'form')])

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('is_landed_costs_line', 'product_id')
    def _onchange_is_landed_costs_line_new(self):
        if self.product_id:
            accounts = self.product_id.product_tmpl_id._get_product_accounts()
            if self.product_type != 'service':
                self.account_id = accounts['expense']
                self.is_landed_costs_line = False
            elif self.is_landed_costs_line and self.move_id.company_id.anglo_saxon_accounting:

                if accounts['stock_input']:
                    self.account_id = accounts['stock_input']
                else:
                    self.account_id = self.product_id.property_account_income_id.id
            else:
                print('Account 2 :: ', accounts)
                if accounts['expense']:
                    self.account_id = accounts['expense']
                else:
                    self.account_id = self.product_id.property_account_expense_id.id
