# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import json

class Sale(models.Model):
    _inherit = 'sale.order'

    show_request_bom = fields.Boolean(string='Show Request BOM', compute="set_show_request_bom")
    bom_request_id = fields.Many2one('bom.request', string='BOM Request', copy=False)
    total_delivered = fields.Float(string='Delivered', compute='get_total_delivered')
    state = fields.Selection(selection_add=[('bom_requested', 'BOM Requested'),('dm_approve', 'To DM Approve'),('sm_approve', 'To SM Approve'),('sent', 'Quotation Sent'),('approve','Approved'),('sale','Sales Order')])
    discount_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')], string='Discount Type',
                                     readonly=True, states={'draft': [('readonly', False)]}, default='percent')
    discount_rate = fields.Float(string="Discount Rate")
    amount_discount = fields.Monetary(string="Discount", compute='_compute_net_total')
    price_before_discount = fields.Monetary('Price B/f Disc', compute='_compute_net_total', store=True)
    discount_tax = fields.Many2one('account.tax', string='Discount Tax',
                                   default=lambda self: self.env.company.account_sale_tax_id)
    global_discount_tax = fields.Monetary(string='Discount Tax amount', store=True, readonly=True, tracking=True,
                                          compute='_compute_discount_tax')

    @api.depends('discount_rate', 'discount_tax', 'amount_discount')
    def _compute_discount_tax(self):
        for move in self:
            move.global_discount_tax = 0
            if move.discount_tax and move.amount_discount > 0:
                move.global_discount_tax = (move.amount_discount * move.discount_tax.amount) / 100

    @api.depends('order_line')
    def get_total_delivered(self):
        total_delivered = 0.0
        for line in self.order_line:
            total_delivered += line.qty_delivered
        self.total_delivered = total_delivered

    def action_confirm(self):
        if not self.env.user.has_group('khalifa_customizations.sale_order_approval'):
            raise ValidationError(_("You are not allow to do this operation."))
        # check if user is accounting manager or admin if yes then skip
        acc_advisor = self.env.user.has_group('account.group_account_manager')
        admin = self.env.user.has_group('base.group_erp_manager')
        if not (acc_advisor or admin):
            self.validate_customer()
        # do not confirm if the product in order lines is non-standard bom product
        self.validate_order_line()
        res = super().action_confirm()
        return res

    def action_cancel(self):
        res = super().action_cancel()
        # if the order is canceled then remove relationship to BOM request
        self.bom_request_id.cancel_dummy_bom()
        self.bom_request_id.write({
            'state':'cancel'
        })
        self.write({
            'bom_request_id': False,
        })
        for line in self.order_line:
            line.bom_id = False
            line.drawing = ''
        return res

    def validate_order_line(self):
        for line in self.order_line:
            if line.product_id.non_standard_bom and not line.bom_id:
                raise ValidationError("Assign BOM in order line where product '%s' is added."%(line.product_id.name))
            if line.product_id.standard_bom and not line.bom_id:
                raise ValidationError("Assign Standard BOM in order line where product '%s' is added."%(line.product_id.name))

    def action_quotation_send(self):
        acc_advisor = self.env.user.has_group('account.group_account_manager')
        admin = self.env.user.has_group('base.group_erp_manager')
        if not (acc_advisor or admin):
            self.validate_customer()
        res = super().action_quotation_send()
        return res

    def action_view_bom_request(self):
        bom_requests = self.mapped('bom_request_id')
        context = {
            'id': bom_requests.id,
        }
        return {
            'type': 'ir.actions.act_window',
            'name': 'BOM Request',
            'view_mode': 'form,tree',
            'res_model': 'bom.request',
            'res_id' : bom_requests.id,
            'domain': [('id', '=', bom_requests.id)],
            'context': context
        }

    def validate_customer(self):
        query = """
            SELECT id
            FROM account_move
            WHERE invoice_date < current_date - interval '90' day
            AND move_type = 'out_invoice'
            AND payment_state IN ('not_paid','partial')
            AND partner_id = %s;
        """%(self.partner_id.id)
        self._cr.execute(query)
        result = self._cr.dictfetchall()
        if result:
            raise ValidationError("Unpaid invoice(s) exist for this customer before 90 days.")

    def action_sm_approve(self):
        if self.env.user.has_group('khalifa_customizations.sale_order_approval'):
            self.write({
                'state': 'approve'
            })
        else:
            raise ValidationError(_("Only Design Manager can approve this quotation."))
    
    def action_to_sm_approve(self):
        # do not confirm if the product in order lines is non-standard bom product
        self.validate_order_line()
        self.write({
            'state': 'sm_approve'
        })

    def request_bom(self):
        product_data = self.get_non_standard_prd_data()
        values = {
            'order_id': self.id,
            'bom_request_line_ids':product_data
        }
        bom_request_id = self.create_bom_request(values)
        self.write({
            'bom_request_id': bom_request_id.id,
            'state': 'bom_requested'
        })

    def create_bom_request(self, values):
        BOMRequest = self.env['bom.request']
        return BOMRequest.create(values)
    
    def get_non_standard_prd_data(self):
        data = []
        for line in self.order_line:
            if line.product_id.non_standard_bom:
                data.append((0,0,{
                    'product_id': line.product_id.id,
                    'description': line.name,
                    'label': line.label,
                    'drawing': line.drawing,
                    'sec_wh_id': line.sec_wh_id and line.sec_wh_id.id,
                    'line_no': line.line_no,
                    'quantity': line.product_uom_qty,
                    'product_uom_id': line.product_uom.id,
                    'order_line_id': line.id
                }))
        return data

    @api.depends('order_line.product_id', 'order_line.bom_id')
    def set_show_request_bom(self):
        show = False
        if self.state not in ['sale','done','cancel'] and not self.bom_request_id:
            for line in self.order_line:
                if line.product_id.non_standard_bom and not line.bom_id:
                    show = True
        self.show_request_bom = show

    @api.depends('order_line.price_total','amount_discount')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed - order.amount_discount,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax - order.amount_discount - order.global_discount_tax,
            })


    # discount
    @api.depends('discount_rate', 'amount_total', 'discount_type')
    def _compute_net_total(self):
        for sale in self:
            sale.amount_discount = price_before_discount = discount = 0
            for line in sale.order_line:
                price_before_discount += line.price_before_discount
                discount += line.discount_amount

            sale.price_before_discount = price_before_discount
            if sale.discount_type == 'amount':
                if sale.discount_rate <= sale.price_before_discount:
                    sale.amount_discount = discount + sale.discount_rate
                else:
                    raise ValidationError(_("Discount Cannot be more than Total"))
            if sale.discount_type == 'percentage':
                if sale.discount_rate <= 100:
                    sale.amount_discount = discount + ((sale.price_before_discount * sale.discount_rate) / 100)
                else:
                    raise ValidationError(_("Discount rate cannot be more than 100%"))
            print(sale.amount_discount)

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        def compute_taxes(order_line):
            price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
            order = order_line.order_id
            return order_line.tax_id._origin.compute_all(price, order.currency_id, order_line.product_uom_qty,
                                                         product=order_line.product_id,
                                                         partner=order.partner_shipping_id)

        account_move = self.env['account.move']
        for order in self:
            if order.discount_type == 'amount':
                if order.discount_tax:
                    discount_tax = (order.discount_rate * order.discount_tax.amount) / 100
                else:
                    discount_tax = 0
            elif order.discount_type == 'percentage':
                if order.discount_tax:
                    discount = order.price_before_discount * ((order.discount_rate or 0.0) / 100.0)
                    discount_tax = (discount * order.discount_tax.amount) / 100
                else:
                    discount_tax = 0
            else:
                discount_tax = 0
            tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line,
                                                                                         compute_taxes)
            if discount_tax > 0:
                tax_totals = account_move._get_tax_totals_new(order.partner_id, tax_lines_data, order.amount_total,
                                                      order.amount_untaxed, order.currency_id,discount_tax)
            else:
                tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total,
                                                          order.amount_untaxed, order.currency_id)
            order.tax_totals_json = json.dumps(tax_totals)


    def _prepare_invoice(self, ):
        invoice_vals = super(Sale, self)._prepare_invoice()
        invoice_vals.update({
            'discount_type': self.discount_type,
            'discount_rate': self.discount_rate,
            'amount_discount': self.amount_discount,
            'discount': self.amount_discount,
            'discount_tax': self.discount_tax.id,
        })
        return invoice_vals

    # def _create_invoices(self, grouped=False, final=False, date=None):
    #     res = super(Sale, self)._create_invoices()
    #     print('Invoices :: ',res)
    #     res.supply_rate()
    #     return res
#
#
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_amount = fields.Float('Discount Amount', compute='_compute_all_price', store=True)
    price_before_discount = fields.Monetary('Price B/f Disc', compute='_compute_all_price', store=True)

    @api.depends('discount', 'price_unit', 'product_uom_qty')
    def _compute_all_price(self):
        for line in self:
            line.price_before_discount = line.product_uom_qty * line.price_unit
            line.discount_amount = (line.price_before_discount * line.discount) / 100.0

# class SaleAdvancePaymentInv(models.TransientModel):
#     _inherit = "sale.advance.payment.inv"



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
