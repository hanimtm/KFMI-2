# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class StockAnalyticLocation(models.Model):
    _name = "stock.analytic.location"
    _description = 'Analytic account in Location'

    name = fields.Char('Name')
    location_id = fields.Many2one('stock.location', string="Location")
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)',
         'Name is already available, Please use another name !!!'),
    ]
