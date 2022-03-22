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


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    branch_id = fields.Many2one('company.branch', string="Branch")
    test_field = fields.Char("test field")

    def _select(self):
        res = super(PurchaseReport, self)._select() + ", po.branch_id as branch_id"
        return res

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", po.branch_id"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
