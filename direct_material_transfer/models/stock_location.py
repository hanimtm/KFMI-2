# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError,UserError
from odoo.tools import float_is_zero


class StockLocation(models.Model):
    _inherit = "stock.location"

    expense_account = fields.Many2one(
        'account.account',
        string="Expense Account",
    )
