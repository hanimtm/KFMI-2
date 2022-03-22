# -*- coding:utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_option = fields.Selection([('cash','Cash'),('bank','Bank'),('mixed','Mixed')], string="Payment Options", default='cash')
    cash_journal_id = fields.Many2one('account.journal', string='Cash Journal', domain="[('company_id', '=', company_id), ('type','=','cash')]")
    cash_amount = fields.Float(string='Cash Amount')
    bank_journal_id = fields.Many2one('account.journal', string='Bank Journal', domain="[('company_id', '=', company_id), ('type','=','bank')]")
    bank_amount = fields.Float(string='Bank Amount')
    show_register_payment = fields.Boolean(string='Show Register Payment', compute='get_show_register_payment')

    @api.depends('state','payment_state','move_type')
    # ['|', '|', ('state', '!=', 'posted'), ('payment_state', 'not in', ('not_paid', 'partial')), ('move_type', 'not in', ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt'))]
    def get_show_register_payment(self):
        show = True
        if self.state != 'posted' or self.payment_state not in ['not_paid', 'partial'] or self.move_type not in ['out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt']:
            show = False
        else:
            if self.env.user.has_group('amcl_invoice_customizations.group_show_cash_bank_payment') and self.move_type in ['out_invoice']:
                show = False
            else:
                show = True
        self.show_register_payment = show


    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if res.get('move_type','') == 'out_invoice':
            cash_journal_id = self.env['ir.config_parameter'].sudo().get_param('invoice_cash_journal_id')
            bank_journal_id = self.env['ir.config_parameter'].sudo().get_param('invoice_bank_journal_id')
            res.update({
                'cash_journal_id': False if not cash_journal_id else int(cash_journal_id),
                'bank_journal_id': False if not bank_journal_id else int(bank_journal_id),
            })
        return res

    @api.onchange('payment_option')
    def onchange_payment_option(self):
        if self.payment_option == 'cash':
            cash_journal_id = self.env['ir.config_parameter'].sudo().get_param('invoice_cash_journal_id')
            self.write({
                'cash_journal_id': False if not cash_journal_id else int(cash_journal_id),
                'cash_amount': 0.0,
                'bank_journal_id': False,
                'bank_amount': 0.0,
            })
        elif self.payment_option == 'bank':
            bank_journal_id = self.env['ir.config_parameter'].sudo().get_param('invoice_bank_journal_id')
            self.write({
                'cash_journal_id': False,
                'cash_amount': 0.0,
                'bank_journal_id': False if not bank_journal_id else int(bank_journal_id),
                'bank_amount': 0.0,
            })
        elif self.payment_option == 'mixed':
            cash_journal_id = self.env['ir.config_parameter'].sudo().get_param('invoice_cash_journal_id')
            bank_journal_id = self.env['ir.config_parameter'].sudo().get_param('invoice_bank_journal_id')
            self.write({
                'cash_journal_id': False if not cash_journal_id else int(cash_journal_id),
                'cash_amount': 0.0,
                'bank_journal_id': False if not bank_journal_id else int(bank_journal_id),
                'bank_amount': 0.0,
            })

    def get_payment_option_values(self):
        values = {
            'default_payment_option': self.payment_option,
            'default_cash_journal_id': False if not self.cash_journal_id else self.cash_journal_id.id,
            'default_cash_amount': self.cash_amount,
            'default_bank_journal_id': False if not self.bank_journal_id else self.bank_journal_id.id,
            'default_bank_amount': self.bank_amount,
            'default_cash_memo': self.name,
            'default_bank_memo': self.name,
        }
        return values
        
    def action_register_with_payment_options(self):
        values = self.get_payment_option_values()
        values.update({
                'active_model': 'account.move',
                'active_ids': self.ids,
            })
        return {
            'name': _('Register Payment'),
            'res_model': 'amcl.payment.register',
            'view_mode': 'form',
            'context': values,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
