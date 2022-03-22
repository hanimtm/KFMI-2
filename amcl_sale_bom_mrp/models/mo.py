# -*- coding : utf-8 -*-

from odoo import models, fields, api


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    work_in_progress = fields.Many2one('account.account','Work In Progress (account)',required=True)
    labor_cost = fields.Many2one('account.account','Labor Cost (account)',required=True)
    stock_journal = fields.Many2one('account.journal', 'Stock Journal',required=True)

class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    account_move_id = fields.Many2one('account.move', "Journal Entry")

    def _create_or_update_analytic_entry(self):
        res = super(MrpWorkorder, self)._create_or_update_analytic_entry()
        for data in self:
            hours = data.duration / 60.0
            value = hours * data.workcenter_id.costs_hour
            debit_account = data.workcenter_id.work_in_progress.id
            credit_account = data.workcenter_id.labor_cost.id
            if not data.account_move_id:
                move = self.env['account.move'].create({
                    'name': '/',
                    'journal_id': data.workcenter_id.stock_journal.id,
                    'date': fields.Date.today(),
                    'ref': data.production_id.name,
                    'line_ids': [(0, 0, {
                        'account_id': credit_account,
                        'credit': value,
                        'debit': 0,
                        'name': 'Labor cost for ' + data.production_id.name,
                    }), (0, 0, {
                        'account_id': debit_account,
                        'debit': value,
                        'credit': 0,
                        'name': 'Labor cost for ' + data.production_id.name,
                    })]
                })
                data.account_move_id = move.id
            else:
                if data.account_move_id.amount_total == 0:
                    credit_line_id = data.account_move_id.line_ids[0]
                    debit_line_id = data.account_move_id.line_ids[1]
                    data.account_move_id[0].write({
                        'line_ids': [
                            (1, credit_line_id.id, {'credit': value}),
                            (1, debit_line_id.id, {'debit': value}),
                        ]
                    })
                else:
                    credit_line_id = data.account_move_id.line_ids.filtered(lambda x: x.debit == 0)
                    debit_line_id = data.account_move_id.line_ids.filtered(lambda x: x.credit == 0)

                    print(data.account_move_id)
                    print(credit_line_id)
                    print(debit_line_id)

                    data.account_move_id[0].write({
                        'line_ids': [
                            (1, credit_line_id.id, {'credit': value}),
                            (1, debit_line_id.id, {'debit': value}),
                        ]
                    })
        return res