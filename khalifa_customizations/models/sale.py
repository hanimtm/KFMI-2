# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class Sale(models.Model):
    _inherit = 'sale.order'

    show_request_bom = fields.Boolean(string='Show Request BOM', compute="set_show_request_bom")
    bom_request_id = fields.Many2one('bom.request', string='BOM Request', copy=False)
    total_delivered = fields.Float(string='Delivered', compute='get_total_delivered')
    state = fields.Selection(selection_add=[('bom_requested', 'BOM Requested'),('dm_approve', 'To DM Approve'),('sm_approve', 'To SM Approve'),('sent', 'Quotation Sent'),('approve','Approved'),('sale','Sales Order')])

    # discount
    discount_type = fields.Selection([('fixed_amount', 'Fixed Amount'),
                                      ('percentage_discount', 'Percentage')],
                                     string="Discount Type")
    discount_rate = fields.Float(string="Discount Rate")
    discount = fields.Monetary(string="Discount", compute='_compute_net_total')
    net_total = fields.Monetary(string="Net Total", compute='_compute_net_total')

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

    # discount
    @api.depends('discount_rate', 'amount_total', 'discount_type')
    def _compute_net_total(self):
        if self.discount_type == 'fixed_amount':
            if self.discount_rate <= self.amount_total:
                self.discount = self.discount_rate
            else:
                raise ValidationError(_("Discount Cannot be more than Total"))
        elif self.discount_type == 'percentage_discount':
            if self.discount_rate <= 100:
                self.discount = (self.amount_total * self.discount_rate) / 100
            else:
                raise ValidationError(_("Discount rate cannot be more than 100%"))
        self.net_total = (self.amount_total - self.discount)

    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        for invoice in invoices:
            invoice.discount_type = self.discount_type
            invoice.discount_rate = self.discount_rate
            invoice.discount = self.discount
            invoice.net_total = self.net_total
        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.partner_id.id,
                'default_partner_shipping_id': self.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.payment_term_id.id,
                'default_invoice_origin': self.mapped('name'),
                'default_user_id': self.user_id.id,
            })
        action['context'] = context
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
