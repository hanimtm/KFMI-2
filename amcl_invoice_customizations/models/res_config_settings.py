# -*- coding:utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_cash_journal_id = fields.Many2one('account.journal', string='Invoice Cash Journal', domain="[('company_id', '=', company_id), ('type','=','cash')]")
    invoice_bank_journal_id = fields.Many2one('account.journal', string='Invoice Bank Journal', domain="[('company_id', '=', company_id), ('type','=','bank')]")
    bank_charge_account = fields.Many2one('account.account', string='Default Bank Charge Account', domain="[('company_id', '=', company_id)]")

    def get_values(self):
        res = super().get_values()
        res.update({'invoice_cash_journal_id': 
                            int(self.env['ir.config_parameter'].sudo().get_param('invoice_cash_journal_id')) or False,
                    'invoice_bank_journal_id': 
                            int(self.env['ir.config_parameter'].sudo().get_param('invoice_bank_journal_id'))or False,
                    'bank_charge_account':
                            int(self.env['ir.config_parameter'].sudo().get_param('bank_charge_account'))or False,})
        return res

    def set_values(self):
        res = super().set_values()
        if self.invoice_cash_journal_id:
            self.env['ir.config_parameter'].sudo().set_param('invoice_cash_journal_id',
                                                                 self.invoice_cash_journal_id.id or False)
        if self.invoice_bank_journal_id:
            self.env['ir.config_parameter'].sudo().set_param('invoice_bank_journal_id',
                                                                self.invoice_bank_journal_id.id or False)
        if self.bank_charge_account:
            self.env['ir.config_parameter'].sudo().set_param('bank_charge_account',
                                                                self.bank_charge_account.id or False)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
