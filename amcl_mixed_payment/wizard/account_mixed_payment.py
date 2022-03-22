# -*- coding:utf-8 -*-
from odoo import api, fields, models, _


class AccountMixedPayment(models.TransientModel):
    _name = 'account.mixed.payment'
    _description = "Account Mixed Payment"

    @api.depends('company_id')
    def get_currency(self):
        for rec in self:
            if rec.company_id and rec.company_id.currency_id:
                rec.currency_id = rec.company_id.currency_id.id

    date = fields.Date('Date', default=fields.Date.today)
    payment_type = fields.Selection(
        [('inbound', 'Receive'), ('outbound', 'Send')], required=True,
        default='inbound')
    partner_id = fields.Many2one('res.partner', 'Customer')
    company_id = fields.Many2one(
        'res.company', required=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        compute=get_currency,
        help="The payment's currency.")
    ref = fields.Char('Reference')

    cash_amount = fields.Monetary(
        currency_field='currency_id', string="Cash Amount")
    bank_amount = fields.Monetary(
        currency_field='currency_id', string="Bank Amount")

    cash_journal_id = fields.Many2one(
        'account.journal',
        string='Cash Journal',
        domain="[('type', '=', 'cash'), ('company_id', '=', company_id)]",
        check_company=True)

    bank_journal_id = fields.Many2one(
        'account.journal',
        string='Bank Journal',
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]",
        check_company=True)

    def create_mixed_payment(self):
        """
        create mixed Payment (Bank & Cash)
        :return:
        """
        payment_obj = self.env['account.payment']
        vals = {
            'payment_type': self.payment_type,
            'partner_id': self.partner_id and self.partner_id.id or False,
            'date': self.date,
            'state': 'draft',
            'ref': self.ref,
        }
        if self.cash_amount > 0 and self.cash_journal_id:
            # Create Cash Payment
            vals.update({
                'amount': self.cash_amount,
                'journal_id': self.cash_journal_id and
                              self.cash_journal_id.id or False
            })
            cash_rec = payment_obj.create(vals)
        if self.bank_amount > 0 and self.bank_journal_id:
            # Creare Bank Payment
            vals.update({
                'amount': self.bank_amount,
                'journal_id': self.bank_journal_id and
                              self.bank_journal_id.id or False
            })
            bank_payment_rec = payment_obj.create(vals)
            print('\n\n\n =====>>> ', bank_payment_rec)