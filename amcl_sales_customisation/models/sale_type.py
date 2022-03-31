# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class SaleType(models.Model):
    _name = 'sale.type'
    _description = 'Sale Type'

    name = fields.Char(string='Sales Type')
    income_account = fields.Many2one('account.account', string='Income Account', index=True, ondelete="cascade")
    expense_account = fields.Many2one('account.account', string='Expense Account',
                                      index=True, ondelete="cascade")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)






