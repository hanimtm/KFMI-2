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

from odoo import models, fields


class SaleReport(models.Model):
    _inherit = "sale.report"

    branch_id = fields.Many2one('company.branch', string="Branch")

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['branch_id'] = ", s.branch_id as branch_id"
        groupby += ', s.branch_id'
        res = super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
