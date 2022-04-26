# -*- coding:utf-8 -*-
from odoo import fields, models, api


class AccountAccount(models.Model):
    _inherit = 'account.group'

    name = fields.Char(required=True, translate=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
