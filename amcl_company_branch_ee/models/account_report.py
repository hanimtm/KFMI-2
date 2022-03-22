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

from odoo import models, fields, api

class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_branches = True

    @api.model
    def _get_filter_branches(self):
        branch_ids =  self.env['company.branch'].search([
            ('company_id', 'in', self.env.user.company_ids.ids or [self.env.company.id]),
            ('id','in', self.env.user.branch_ids.ids or [self.env.user.branch_id.id])
            ], order="company_id, name")
        return branch_ids

    @api.model
    def _init_filter_branches(self, options, previous_options=None):
        if self.filter_branches is None:
            return

        previous_company = False
        if previous_options and previous_options.get('branches'):
            branch_map = dict((opt['id'], opt['selected']) for opt in previous_options['branches'] if opt['id'] != 'divider' and 'selected' in opt)
        else:
            branch_map = {}

        options['branches'] = []
        for branch in self._get_filter_branches():
            if branch.company_id != previous_company:
                options['branches'].append({'id': 'divider', 'name': branch.company_id.name})
                previous_company = branch.company_id
            options['branches'].append({
                'id': branch.id,
                'name': branch.name,
                'parent_id': branch.parent_id,
                'selected': branch_map.get(branch.id),
            })

    @api.model
    def _get_options_branches(self, options):
        return [
            branch for branch in options.get('branches', []) if
            not branch['id'] in ('divider', 'group') and branch['selected']
        ]

    @api.model
    def _get_options_branches_domain(self, options):
        # Make sure to return an empty array when nothing selected to handle archived branches.
        selected_branches = self._get_options_branches(options)
        return selected_branches and [('branch_id', 'in', [b['id'] for b in selected_branches])] or []

    @api.model
    def _get_options_domain(self, options):
        domain = super(AccountReport, self)._get_options_domain(options)
        domain += self._get_options_branches_domain(options)
        return domain


class AccountingReport(models.AbstractModel):
    _inherit = 'account.accounting.report'

    filter_branches = True

    branch_id = fields.Many2one('company.branch')

    def _get_move_line_fields(self, aml_alias="account_move_line"):
        return ', '.join('%s.%s' % (aml_alias, field) for field in (
            'id',
            'move_id',
            'name',
            'account_id',
            'journal_id',
            'company_id',
            'currency_id',
            'analytic_account_id',
            'display_type',
            'date',
            'debit',
            'credit',
            'balance',
            'branch_id'
        ))
