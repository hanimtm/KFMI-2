# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount type',
    #                                  readonly=True,
    #                                  states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
    #                                  default='percent')
    discount_type = fields.Selection([('fixed_amount', 'Fixed Amount'),
                                      ('percentage_discount', 'Percentage')],
                                     string="Discount Type",
                                     readonly=True,
                                     # states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                     )

    discount_rate = fields.Float('Discount Rate', digits=dp.get_precision('Account'),
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, )
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all_new',
                                     track_visibility='onchange')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all_new',
                                 track_visibility='onchange')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all_new',
                                   track_visibility='onchange')
    price_before_discount = fields.Monetary('Total ( Excluded VAT)', compute='_amount_all_new', store=True,
                                            readonly=True)
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_amount_all_new',
                                      digits=dp.get_precision('Account'), track_visibility='onchange')
    revision = fields.Char(string='Revision')

    @api.depends('order_line.price_total', 'discount_rate')
    def _amount_all_new(self):
        for order in self:
            price_before_discount = amount_discount = amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                print("Line Tax :: ", line.price_tax)
                amount_discount += line.discount_amount
                price_before_discount += line.price_before_discount
            currency = order.currency_id or order.partner_id.property_purchase_currency_id or self.env.company.currency_id
            order.update({
                'amount_untaxed': currency.round(amount_untaxed),
                'amount_tax': currency.round(amount_tax),
                'price_before_discount': currency.round(price_before_discount),
                'amount_discount': currency.round(amount_discount),
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.onchange('discount_type', 'discount_rate')
    def _onchange_discount(self):
        for order in self:
            if order.discount_type == 'percentage_discount':
                for line in order.order_line:
                    line.discount = order.discount_rate
                # order.amount_discount = (order.amount_untaxed * order.discount_rate)/100
            else:
                total = discount = 0.0
                for line in order.order_line:
                    total += round((line.product_qty * line.price_unit))
                if order.discount_rate != 0 and total > 0:
                    discount = (order.discount_rate / total) * 100
                else:
                    discount = order.discount_rate
                for line in order.order_line:
                    line.discount = discount

    def _prepare_invoice(self, ):
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        discout_type = False
        if self.discount_type == 'percentage_discount':
            discout_type = 'percentage_discount'
        if self.discount_type == 'fixed_amount':
            discout_type = 'fixed_amount'

        invoice_vals.update({
            'discount_type': discout_type,
            'discount_rate': self.discount_rate,
        })
        print('Invoice Values :: ', invoice_vals)
        return invoice_vals

    def button_dummy(self):
        self.supply_rate()
        return True
