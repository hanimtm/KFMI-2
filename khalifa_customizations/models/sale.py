# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import json
import odoo.addons.decimal_precision as dp

class Sale(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = amount_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amount_discount += (line.product_uom_qty * line.price_unit * line.discount) / 100
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_discount': amount_discount,
                'amount_total': amount_untaxed + amount_tax,
            })

    show_request_bom = fields.Boolean(string='Show Request BOM', compute="set_show_request_bom")
    bom_request_id = fields.Many2one('bom.request', string='BOM Request', copy=False)
    total_delivered = fields.Float(string='Delivered', compute='get_total_delivered')
    state = fields.Selection(selection_add=[('bom_requested', 'BOM Requested'),('dm_approve', 'To DM Approve'),('sm_approve', 'To SM Approve'),('sent', 'Quotation Sent'),('approve','Approved'),('sale','Sales Order')])
    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount type',
                                     readonly=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                     default='percent')
    discount_rate = fields.Float('Discount Rate', digits=dp.get_precision('Account'),
                                 readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all',
                                 track_visibility='always')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all',
                                   track_visibility='always')
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_amount_all',
                                      digits=dp.get_precision('Account'), track_visibility='always')

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

    @api.onchange('discount_type', 'discount_rate', 'order_line')
    def supply_rate(self):

        for order in self:
            if order.discount_type == 'percent':
                for line in order.order_line:
                    line.discount = order.discount_rate
            else:
                total = discount = 0.0
                for line in order.order_line:
                    total += round((line.product_uom_qty * line.price_unit))
                if order.discount_rate != 0:
                    discount = (order.discount_rate / total) * 100
                else:
                    discount = order.discount_rate
                for line in order.order_line:
                    line.discount = discount

    def _prepare_invoice(self, ):
        invoice_vals = super(Sale, self)._prepare_invoice()
        invoice_vals.update({
            'discount_type': self.discount_type,
            'discount_rate': self.discount_rate,
        })
        return invoice_vals

    def button_dummy(self):

        self.supply_rate()
        return True

    # def _create_invoices(self, grouped=False, final=False, date=None):
    #     res = super(Sale, self)._create_invoices()
    #     print('Invoices :: ',res)
    #     res.supply_rate()
    #     return res
#
#
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount = fields.Float(string='Discount (%)', digits=(16, 20), default=0.0)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
