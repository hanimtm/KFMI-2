# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockLandedCostInherit(models.Model):
	_inherit = "stock.landed.cost"
	_description = "Stock Landed Cost"


	def button_done_cancel(self):
		for cost in self:
			move = self.env['account.move'].browse(cost.account_move_id.id)
			rec_ids = move.line_ids._reconciled_lines()
			self.env['account.move.line'].browse(rec_ids).remove_move_reconcile()
			move.with_context(force_delete=True).unlink()

			valuation_ids = self.env['stock.valuation.layer'].search([('stock_landed_cost_id','=',cost.id)])
			valuation_ids.sudo().unlink()

			AdjustementLines = self.env['stock.valuation.adjustment.lines']
			AdjustementLines.search([('cost_id', '=', cost.id)]).unlink()
		return self.write({'state': 'cancel'})
		

	def button_set_draft(self):
		if any(cost.state != 'cancel' or cost.state == 'draft' for cost in self):
			raise UserError(
				_('Landed costs which are not in cancel state or already in draft state cannot be set to draft state.'))
		return self.write({'state': 'draft'})


	def action_view_moves(self):
		self.ensure_one()
		return {
            'type': 'ir.actions.act_window',
            'name': _('Journal Entries'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id','=',self.account_move_id.id)],
        }



