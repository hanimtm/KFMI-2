from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    bank_charge_line = fields.Boolean('Its a Bank Charge')

class PaymentRegisterOption(models.TransientModel):
    _name = 'amcl.payment.register'
    _description = 'Payment Register'

    @api.model
    def _bank_charge_account(self):
        account = self.env['ir.config_parameter'].sudo().get_param('bank_charge_account')
        return int(account)

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    payment_option = fields.Selection([('cash','Cash'),('bank','Bank'),('mixed','Mixed')], string="Payment Options", default='cash')
    cash_journal_id = fields.Many2one('account.journal', string='Cash Journal', domain="[('company_id', '=', company_id), ('type','=','cash')]")
    cash_amount = fields.Float(string='Cash Amount')
    bank_journal_id = fields.Many2one('account.journal', string='Bank Journal', domain="[('company_id', '=', company_id), ('type','=','bank')]")
    bank_amount = fields.Float(string='Bank Amount')

    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today)
    cash_memo = fields.Char(string='Cash Memo')
    bank_memo = fields.Char(string='Bank Memo')

    is_bank_charges = fields.Boolean('Add Bank Changes')
    bank_charges_account = fields.Many2one('account.account', string='Bank Charges Account', default=_bank_charge_account,)
    bank_charges = fields.Float(string='Bank Charges')

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
            bank_amount = self.bank_amount
            values.update({
                    'journal_id': self.bank_journal_id.id,
                    'amount': bank_amount,
                    'communication': self.bank_memo,
                })
            if self.is_bank_charges:
                values.update({
                    'is_bank_charges':self.is_bank_charges,
                    'bank_charges_account': self.bank_charges_account.id,
                    'bank_charges': self.bank_charges,
                })
            payment_ids += self.env['account.payment.register'].create(values)
        for payment in payment_ids:
            payment.with_context(dont_redirect_to_payments=True).action_create_payments()


class PaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.model
    def _bank_charge_account(self):
        account = self.env['ir.config_parameter'].sudo().get_param('bank_charge_account')
        return int(account)

    is_bank_charges = fields.Boolean('Add Bank Changes')
    bank_charges_account = fields.Many2one('account.account', string='Bank Charges Account', default=_bank_charge_account)
    bank_charges = fields.Float(string='Bank Charges')
    journal_type = fields.Selection(related='journal_id.type', store=True)

    def _create_payment_vals_from_wizard(self):
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_line_id': self.payment_method_line_id.id,
            'destination_account_id': self.line_ids[0].account_id.id,
            'is_bank_charges': self.is_bank_charges,
            'bank_charges_account': self.bank_charges_account.id or False,
            'bank_charges': self.bank_charges or False
        }

        if not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == 'reconcile':
            payment_vals['write_off_line_vals'] = {
                'name': self.writeoff_label,
                'amount': self.payment_difference,
                'account_id': self.writeoff_account_id.id,
            }
        return payment_vals


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def _bank_charge_account(self):
        account = self.env['ir.config_parameter'].sudo().get_param('bank_charge_account')
        return int(account)

    is_bank_charges = fields.Boolean('Add Bank Changes')
    bank_charges_account = fields.Many2one('account.account', string='Bank Charges Account', default=_bank_charge_account)
    bank_charges = fields.Float(string='Bank Charges')
    journal_type = fields.Selection(related='journal_id.type',store=True)


    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}

        if not self.outstanding_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set either on the company or the %s payment method in the %s journal.",
                self.payment_method_line_id.name, self.journal_id.display_name))

        # Compute amounts.
        write_off_amount_currency = write_off_line_vals.get('amount', 0.0)

        if self.payment_type == 'inbound':
            # Receive money.
            liquidity_amount_currency = self.amount
        elif self.payment_type == 'outbound':
            # Send money.
            liquidity_amount_currency = -self.amount
            write_off_amount_currency *= -1
        else:
            liquidity_amount_currency = write_off_amount_currency = 0.0

        write_off_balance = self.currency_id._convert(
            write_off_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        liquidity_balance = self.currency_id._convert(
            liquidity_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
        counterpart_balance = -liquidity_balance - write_off_balance
        currency_id = self.currency_id.id

        if self.is_internal_transfer:
            if self.payment_type == 'inbound':
                liquidity_line_name = _('Transfer to %s', self.journal_id.name)
            else: # payment.payment_type == 'outbound':
                liquidity_line_name = _('Transfer from %s', self.journal_id.name)
        else:
            liquidity_line_name = self.payment_reference

        # Compute a default label to set on the journal items.

        payment_display_name = self._prepare_payment_display_name()

        default_line_name = self.env['account.move.line']._get_default_line_name(
            _("Internal Transfer") if self.is_internal_transfer else payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
            self.amount,
            self.currency_id,
            self.date,
            partner=self.partner_id,
        )

        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name or default_line_name,
                'date_maturity': self.date,
                'amount_currency': liquidity_amount_currency,
                'currency_id': currency_id,
                'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.outstanding_account_id.id,
            },
            # Receivable / Payable.
            {
                'name': self.payment_reference or default_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.destination_account_id.id,
            },
        ]
        print('Is Bank :: ', self.is_bank_charges)
        if self.is_bank_charges:
            line_vals_list.append({
                "name": 'Bank Charges',
                "ref": self.ref,
                "partner_id": self.partner_id.id or False,
                "journal_id": self.journal_id.id,
                "account_id": self.journal_id.default_account_id.id,
                "debit": 0,
                "credit": self.bank_charges,
                "date_maturity": self.date,
                "bank_charge_line": True
            })
            line_vals_list.append({
                    "name": 'Bank Charges',
                    "ref": self.ref,
                    "partner_id": self.partner_id.id or False,
                    "journal_id": self.journal_id.id,
                    "account_id": self.bank_charges_account.id,
                    "debit": self.bank_charges,
                    "credit": 0,
                    "date_maturity": self.date,
                    "bank_charge_line": True
                }
            )

        if not self.currency_id.is_zero(write_off_amount_currency):
            # Write-off line.
            line_vals_list.append({
                'name': write_off_line_vals.get('name') or default_line_name,
                'amount_currency': write_off_amount_currency,
                'currency_id': currency_id,
                'debit': write_off_balance if write_off_balance > 0.0 else 0.0,
                'credit': -write_off_balance if write_off_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': write_off_line_vals.get('account_id'),
            })
        return line_vals_list

    def _synchronize_from_moves(self, changed_fields):
        ''' Update the account.payment regarding its related account.move.
        Also, check both models are still consistent.
        :param changed_fields: A set containing all modified fields on account.move.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):

            # After the migration to 14.0, the journal entry could be shared between the account.payment and the
            # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
            if pay.move_id.statement_line_id:
                continue

            move = pay.move_id
            move_vals_to_write = {}
            payment_vals_to_write = {}

            if 'journal_id' in changed_fields:
                if pay.journal_id.type not in ('bank', 'cash'):
                    raise UserError(_("A payment must always belongs to a bank or cash journal."))

            if 'line_ids' in changed_fields:
                all_lines = move.line_ids
                liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()
                if len(liquidity_lines) != 1 and not pay.is_bank_charges:
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "include one and only one outstanding payments/receipts account.",
                        move.display_name,
                    ))
                if len(liquidity_lines) != 1 and pay.is_bank_charges:
                    liquidity_lines = liquidity_lines.filtered(lambda e: e.bank_charge_line is False)

                if len(counterpart_lines) != 1:
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "include one and only one receivable/payable account (with an exception of "
                        "internal transfers).",
                        move.display_name,
                    ))

                if writeoff_lines and len(writeoff_lines.account_id) != 1:
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, "
                        "all optional journal items must share the same account.",
                        move.display_name,
                    ))

                if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "share the same currency.",
                        move.display_name,
                    ))

                if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "share the same partner.",
                        move.display_name,
                    ))

                if counterpart_lines.account_id.user_type_id.type == 'receivable':
                    partner_type = 'customer'
                else:
                    partner_type = 'supplier'

                liquidity_amount = liquidity_lines.amount_currency

                move_vals_to_write.update({
                    'currency_id': liquidity_lines.currency_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                payment_vals_to_write.update({
                    'amount': abs(liquidity_amount),
                    'partner_type': partner_type,
                    'currency_id': liquidity_lines.currency_id.id,
                    'destination_account_id': counterpart_lines.account_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                if liquidity_amount > 0.0:
                    payment_vals_to_write.update({'payment_type': 'inbound'})
                elif liquidity_amount < 0.0:
                    payment_vals_to_write.update({'payment_type': 'outbound'})

            move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
            pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))

