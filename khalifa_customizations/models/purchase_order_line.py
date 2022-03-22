# -*- coding: utf-8 -*-
from odoo import fields, models, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    source_detail = fields.Char(string='Source Detail')
    discount = fields.Float(string='Discount (%)', digits=(16, 20), default=0.0)
    discount_amount = fields.Float('Discount Amount', compute='_compute_amount', store=True)
    price_before_discount = fields.Monetary('Price B/f Disc', compute='_compute_amount', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            price_before_discount= line.product_uom_qty * line.price_unit
            discount_amount = (price_before_discount * line.discount) / 100.0
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            
            taxes = line.taxes_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
            print('Pirce Tax :: ', taxes['total_included'] - taxes['total_excluded'])
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
                'price_before_discount': price_before_discount,
                'discount_amount': discount_amount,
            })
            

    # @api.depends('discount', 'price_unit', 'product_uom_qty')
    # def _compute_all_price(self):
    #     for line in self:
    #         price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
    #         line.price_before_discount = line.product_uom_qty * line.price_unit
    #         line.discount_amount = (line.price_before_discount * line.discount) / 100.0

    def _prepare_compute_all_values(self):
            self.ensure_one()
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
            return {
                'price_unit': price,
                'currency': self.order_id.currency_id,
                'quantity': self.product_qty,
                'product': self.product_id,
                'partner': self.order_id.partner_id,
            }

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        aml_currency = move and move.currency_id or self.currency_id
        date = move and move.date or fields.Date.today()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': '%s: %s' % (self.order_id.name, self.name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount':self.discount,
            'price_unit': self.currency_id._convert(self.price_unit, aml_currency, self.company_id, date, round=False),
            'tax_ids': [(6, 0, self.taxes_id.ids)],
            'analytic_account_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'purchase_line_id': self.id,
        }
        if not move:
            return res

        if self.currency_id == move.company_id.currency_id:
            currency = False
        else:
            currency = move.currency_id

        res.update({
            'move_id': move.id,
            'currency_id': currency and currency.id or False,
            'date_maturity': move.invoice_date_due,
            'partner_id': move.partner_id.id,
        })
        return res



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
