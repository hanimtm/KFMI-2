# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    discount_type = fields.Selection([('fixed_amount', 'Fixed Amount'),
                                      ('percentage_discount', 'Percentage')],
                                     string="Discount Type")
    discount_rate = fields.Float(string="Discount Rate")
    discount = fields.Monetary(string="Discount", compute='_compute_net_total')
    net_total = fields.Monetary(string="Net Total", compute='_compute_net_total')
    revision = fields.Char(string='Revision')

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

    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'in_invoice')
        journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        if not journal:
            raise ValidationError(_('Please define an accounting purchase journal for the company %s (%s).') % (
            self.company_id.name, self.company_id.id))

        partner_invoice_id = self.partner_id.address_get(['invoice'])['invoice']
        invoice_vals = {
            'ref': self.partner_ref or '',
            'move_type': move_type,
            'narration': self.notes,
            'currency_id': self.currency_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'partner_id': partner_invoice_id,
            'fiscal_position_id': (
                        self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(partner_invoice_id)).id,
            'payment_reference': self.partner_ref or '',
            'partner_bank_id': self.partner_id.bank_ids[:1].id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
        }
        if self.discount_rate and self.discount_type:
            invoice_vals.update({
                'discount_rate': self.discount_rate,
                'discount_type': self.discount_type,
                'discount': self.discount
            })
        return invoice_vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4