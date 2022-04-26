# -*- coding:utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('amount_total', 'discount_rate', 'discount_type')
    def _compute_net_total(self):
        for each in self:
            if each.amount_total > 0:
                if each.discount_type == 'fixed_amount':
                    if each.discount_rate <= each.amount_total:
                        each.discount = each.discount_rate
                    else:
                        raise UserError(_("Discount Cannot be more than Total"))
                elif each.discount_type == 'percentage_discount':
                    if each.discount_rate <= 100:
                        each.discount = (each.amount_total * each.discount_rate) / 100
                    else:
                        raise UserError(_("Discount rate cannot be more than 100%"))
            each.net_total = each.amount_total - each.discount

    discount_type = fields.Selection([('fixed_amount', 'Fixed Amount'),
                                      ('percentage_discount', 'Percentage')],
                                     string="Discount Type")
    discount_rate = fields.Float(string="Discount Rate")
    discount = fields.Monetary(string="Discount", compute='_compute_net_total')
    net_total = fields.Monetary(string="Net Total", compute='_compute_net_total')

    def action_post(self):
        for move in self:
            # sale = (self.env['sale.order'].browse(self._context.get('active_id')) if move.discount_rate == 0 else move)
            if move and move.move_type == 'out_invoice' and not move.line_ids.filtered(
                    lambda line: line.name == ('Discount Amount')):
                discount_account_id = int(self.env['ir.config_parameter'].sudo().get_param('sales_discount_account_id'))
                if move.discount_rate > 0:
                    if not discount_account_id:
                        raise UserError(_('Please select sale/purchase discount account first in accounting settings.'))
                    else:
                        ml = {'account_id': discount_account_id,
                              'name': 'Discount Amount',
                              'partner_id': move.partner_id.id,
                              'move_id': move.id,
                              'exclude_from_invoice_tab': True,
                              }
                        self.write({'invoice_line_ids': [(0, 0, ml)]})
                # elif sale.discount_rate > 0:
                #     if not discount_account_id:
                #         raise UserError(_('Please select sale/purchase discount account first in accounting settings.'))
                #     else:
                #         ml = {'account_id': discount_account_id,
                #               'name': 'Discount Amount',
                #               'partner_id': move.partner_id.id,
                #               'move_id': move.id,
                #               'exclude_from_invoice_tab': True,
                #               }
                #         self.write({'invoice_line_ids': [(0, 0, ml)]})
            elif move and move.move_type == 'in_invoice' and not move.line_ids.filtered(
                    lambda line: line.name == ('Discount Amount')):
                discount_account_id = int(
                    self.env['ir.config_parameter'].sudo().get_param('purchase_discount_account_id'))
                if move.discount_rate > 0:
                    if not discount_account_id:
                        raise UserError(_('Please select sale/purchase discount account first in accounting settings.'))
                    else:
                        ml = {'account_id': discount_account_id,
                              'name': 'Discount Amount',
                              'partner_id': move.partner_id.id,
                              'move_id': move.id,
                              'exclude_from_invoice_tab': True,
                              }
                        self.write({'invoice_line_ids': [(0, 0, ml)]})
            to_write = {
                'line_ids': []
            }
            if move.move_type == 'in_invoice':
                if move.discount_rate > 0:
                    for line in move.line_ids.filtered(
                            lambda line: line.name == ('Discount Amount')):
                        to_write['line_ids'].append((1, line.id, {'credit': move.discount}))
                    for line in move.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')):
                        to_write['line_ids'].append((1, line.id, {'credit': move.net_total}))
            elif move.move_type == 'out_invoice':
                if move.discount_rate > 0:
                    for line in move.line_ids.filtered(
                            lambda line: line.name == ('Discount Amount')):
                        to_write['line_ids'].append((1, line.id, {'debit': move.discount}))
                    for line in move.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')):
                        to_write['line_ids'].append((1, line.id, {'debit': move.net_total}))
            move.write(to_write)
        rec = super(AccountMove, self).action_post()
        return rec

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
