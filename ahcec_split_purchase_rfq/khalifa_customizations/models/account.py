# -*- coding:utf-8 -*-
from odoo import fields, models, api


class AccountAccount(models.Model):
    _inherit = 'account.account'

    name_arabic = fields.Char(string='Arabic Name')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
