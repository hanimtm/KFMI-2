# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError,UserError
from odoo.tools import float_is_zero


class StockExpense(models.Model):
    _name = "stock.expense.location"
    _description = 'Expense account in Location'

    name = fields.Char(
        'Name'
    )
    location = fields.Many2one(
        'stock.location',
        string="Location",
    )
    expense_account = fields.Many2one(
        'account.account',
        string="Expense Account",
    )

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)',
         'Name is already available, Please use another name !!!'),
    ]
