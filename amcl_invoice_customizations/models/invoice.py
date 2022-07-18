# -*- coding:utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _default_petty_cash_journal(self):
        company_id = self.env.company.id
        return self.env['account.journal'].search([
            ('company_id', '=', company_id),
            ('is_a_petty_cash', '=', True),
        ], limit=1)

    payment_option = fields.Selection([('cash', 'Cash'), ('bank', 'Bank'), ('mixed', 'Mixed')],
                                      string="Payment Options", default='cash')
    cash_journal_id = fields.Many2one('account.journal', string='Cash Journal',
                                      domain="[('company_id', '=', company_id), ('type','=','cash')]")
    cash_amount = fields.Float(string='Cash Amount')
    bank_payment_option = fields.Selection([('atm', 'ATM'), ('bank_transfer', 'Bank Transfer')],
                                      string="Bank Payment By", default='atm')
    bank_journal_id = fields.Many2one('account.journal', string='Bank Journal',
                                      domain="[('company_id', '=', company_id), ('type','=','bank')]")
    bank_amount = fields.Float(string='Bank Amount')
    show_register_payment = fields.Boolean(string='Show Register Payment', compute='get_show_register_payment')
    employee_id = fields.Many2one('hr.employee', 'Employee Petty Cash')
    petty_cash_journal_id = fields.Many2one('account.journal', string='Petty Cash Journal',
                                            default=_default_petty_cash_journal,
                                            domain="[('type', '=', 'general'),('is_a_petty_cash', '=', True)]")
    cash_payment_id = fields.Many2one('account.move', 'Cash Payment Move')

    @api.depends('state', 'payment_state', 'move_type')
    # ['|', '|', ('state', '!=', 'posted'), ('payment_state', 'not in', ('not_paid', 'partial')), ('move_type', 'not in', ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt'))]
    def get_show_register_payment(self):
        show = True
        if self.state != 'posted' or self.payment_state not in ['not_paid', 'partial'] or self.move_type not in [
            'out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt']:
            show = False
        else:
            if self.env.user.has_group(
                    'amcl_invoice_customizations.group_show_cash_bank_payment') and self.move_type in ['out_invoice']:
                show = False
            else:
                show = True
        self.show_register_payment = show

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if res.get('move_type', '') == 'out_invoice':
            cash_journal_id = self.env['ir.config_parameter'].sudo().get_param('invoice_cash_journal_id')
            bank_journal_id = self.env['ir.config_parameter'].sudo().get_param('invoice_bank_journal_id')
            res.update({
                'cash_journal_id': False if not cash_journal_id else int(cash_journal_id),
                'bank_journal_id': False if not bank_journal_id else int(bank_journal_id),
            })
        return res

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        petty_cash_journal_id = self.env['account.journal'].search([
                                ('company_id', '=', self.env.company.id),
                                ('is_a_petty_cash', '=', True),
                            ])
        self.write({'petty_cash_journal_id': petty_cash_journal_id[0].id or False})

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
            'default_bank_payment_option': self.bank_payment_option,
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

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.move_type == 'in_invoice' and self.employee_id and self.petty_cash_journal_id:
            if not self.employee_id.address_home_id:
                raise ValidationError("Please add the Employee Address.")
            cash_journal = self.env['account.move'].create({
                'move_type': 'entry',
                'date': fields.Date.today(),
                'journal_id': self.petty_cash_journal_id.id,
                'ref': self.name,
                'line_ids': [
                    (0, 0, {
                        'name': 'Cash Payment',
                        'debit': self.amount_total,
                        'credit': 0.0,
                        'quantity': 1.0,
                        'currency_id': self.currency_id.id,
                        'account_id': self.partner_id.property_account_payable_id.id,
                        'partner_id': self.commercial_partner_id.id,
                    }),
                    (0, 0, {
                        'name': 'Cash Payment',
                        'credit': self.amount_total,
                        'debit': 0.0,
                        'quantity': 1.0,
                        'currency_id': self.currency_id.id,
                        'account_id': self.petty_cash_journal_id.default_account_id.id,
                        'partner_id': self.employee_id.address_home_id.id
                    }),
                ],
            })



            self.cash_payment_id = cash_journal.id
            self.cash_payment_id._post()
            (self + self.cash_payment_id).line_ids \
                .filtered(lambda line: line.account_internal_type == 'payable') \
                .reconcile()
            # self.sudo().write({'payment_id': cash_payment_id.id})

        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
