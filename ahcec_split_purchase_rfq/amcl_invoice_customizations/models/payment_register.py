from odoo import models, fields, api


class PaymentRegisterOption(models.TransientModel):
    _name = 'amcl.payment.register'
    _description = 'Payment Register'

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    payment_option = fields.Selection([('cash','Cash'),('bank','Bank'),('mixed','Mixed')], string="Payment Options", default='cash')
    cash_journal_id = fields.Many2one('account.journal', string='Cash Journal', domain="[('company_id', '=', company_id), ('type','=','cash')]")
    cash_amount = fields.Float(string='Cash Amount')
    bank_journal_id = fields.Many2one('account.journal', string='Bank Journal', domain="[('company_id', '=', company_id), ('type','=','bank')]")
    bank_amount = fields.Float(string='Bank Amount')

    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today)
    cash_memo = fields.Char(string='Cash Memo')
    bank_memo = fields.Char(string='Bank Memo')

    @api.onchange('payment_option')
    def onchange_payment_option(self):
        if self.payment_option == 'cash':
            self.bank_amount = 0.0
            self.bank_journal_id = False
        elif self.payment_option == 'bank':
            self.cash_amount = 0.0
            self.cash_journal_id = False

    def register_payments(self):
        payment_ids = self.env['account.payment.register']
        if self.payment_option in ['cash','mixed']:
            values = self.env['account.payment.register'].with_context(active_model=self._context.get('active_model'),active_ids=self._context.get('active_ids')).default_get(['line_ids'])
            values.update({
                'journal_id': self.cash_journal_id.id,
                'amount': self.cash_amount,
                'communication': self.cash_memo
            })
            payment_ids += self.env['account.payment.register'].create(values)
        if self.payment_option in ['bank','mixed']:
            values = self.env['account.payment.register'].with_context(active_model=self._context.get('active_model'),active_ids=self._context.get('active_ids')).default_get(['line_ids'])
            values.update({
                'journal_id': self.bank_journal_id.id,
                'amount': self.bank_amount,
                'communication': self.bank_memo
            })
            payment_ids += self.env['account.payment.register'].create(values)
        for payment in payment_ids:
            payment.with_context(dont_redirect_to_payments=True).action_create_payments()
