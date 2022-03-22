# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    branch_id = fields.Many2one('company.branch', string="Branch")

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", line.branch_id as branch_id"

    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + ", move.branch_id as branch_id"

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", move.branch_id"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
