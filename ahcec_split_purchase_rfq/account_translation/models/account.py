# -*- coding:utf-8 -*-
from odoo import fields, models, api


class AccountAccount(models.Model):
    _inherit = 'account.account'

    name = fields.Char(string="Account Name", required=True, index=True, tracking=True, translate=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
