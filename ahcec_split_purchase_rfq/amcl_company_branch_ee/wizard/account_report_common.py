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

from odoo import api, fields, models


class AccountCommonReport(models.TransientModel):
    _inherit = "account.common.report"

    branch_ids = fields.Many2many('company.branch', string="Branch")

    @api.onchange('branch_ids')
    def onchange_branch_ids(self):
        branch_ids = self.env['company.branch'].search([('company_id', '=', self.company_id.id)])
        return {'domain': {'branch_ids': [('id', 'in', branch_ids.ids)]}}

    def _build_contexts(self, data):
        res = super(AccountCommonReport, self)._build_contexts(data)
        res['branch_id'] = data['form']['branch_ids'] if data.get('form', False) and \
                                                         data.get('form', False).get('branch_ids', False) \
            else False
        return res

    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'branch_ids', 'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        return self._print_report(data)


class ReportJournal(models.AbstractModel):
    _inherit = 'report.account.report_journal'

    def lines(self, target_move, journal_ids, sort_selection, data):
        res = super(ReportJournal, self).lines(target_move, journal_ids, sort_selection, data)
        if data['form']['branch_ids']:
            res = res.filtered(lambda l: l.branch_id.id in data['form']['branch_ids'])
        return res.sorted(key=lambda l: l.branch_id.id)

    def _sum_debit(self, data, journal_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[2]
        query = 'SELECT SUM(debit) FROM ' + query_get_clause[0] + \
                ', account_move am WHERE "account_move_line".move_id=am.id ' \
                'AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' '
        if data['form']['branch_ids']:
            query += """AND account_move_line.branch_id IN (%s)""" % (','.join(map(str, data['form']['branch_ids'])))
        self.env.cr.execute(query, params)
        return self.env.cr.fetchone()[0] or 0.0

    def _sum_credit(self, data, journal_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[2]
        query = 'SELECT SUM(credit) FROM ' + query_get_clause[0] + \
                ', account_move am WHERE "account_move_line".move_id=am.id AND' \
                ' am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' '
        if data['form']['branch_ids']:
            query += """AND account_move_line.branch_id IN (%s)""" % (','.join(map(str, data['form']['branch_ids'])))
        self.env.cr.execute(query, params)
        return self.env.cr.fetchone()[0] or 0.0

    def _get_taxes(self, data, journal_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[2]
        query = """
            SELECT rel.account_tax_id, SUM("account_move_line".balance) AS base_amount
            FROM account_move_line_account_tax_rel rel, """ + query_get_clause[0] + """ 
            LEFT JOIN account_move am ON "account_move_line".move_id = am.id
            WHERE "account_move_line".id = rel.account_move_line_id
                AND am.state IN %s
                AND "account_move_line".journal_id IN %s
                AND """ + query_get_clause[1] + """
           """
        if data['form']['branch_ids']:
            query += """ AND account_move_line.branch_id IN (%s)""" % (','.join(map(str, data['form']['branch_ids'])))
        query += """ GROUP BY rel.account_tax_id """
        self.env.cr.execute(query, tuple(params))
        ids = []
        base_amounts = {}
        for row in self.env.cr.fetchall():
            ids.append(row[0])
            base_amounts[row[0]] = row[1]

        res = {}
        for tax in self.env['account.tax'].browse(ids):
            self.env.cr.execute('SELECT sum(debit - credit) FROM ' + query_get_clause[0] +
                                ', account_move am '
                                'WHERE "account_move_line".move_id=am.id AND am.state IN %s AND '
                                '"account_move_line".journal_id IN %s AND '
                                + query_get_clause[1] + ' AND tax_line_id = %s',
                                tuple(params + [tax.id]))
            res[tax] = {
                'base_amount': base_amounts[tax.id],
                'tax_amount': self.env.cr.fetchone()[0] or 0.0,
            }
            if journal_id.type == 'sale':
                # sales operation are credits
                res[tax]['base_amount'] = res[tax]['base_amount'] * -1
                res[tax]['tax_amount'] = res[tax]['tax_amount'] * -1
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
