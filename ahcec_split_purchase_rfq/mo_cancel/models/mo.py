# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models


class Move(models.Model):
    _inherit = 'stock.move'

    def _sh_unreseve_qty(self):
        for move_line in self.sudo().mapped('move_line_ids'):
            # unreserve qty
            quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_id.id),
                                                           ('product_id', '=',
                                                            move_line.product_id.id),
                                                           ('lot_id', '=', move_line.lot_id.id)], limit=1)

            if quant:
                quant.write({'quantity': quant.quantity + move_line.qty_done})

            quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_dest_id.id),
                                                           ('product_id', '=',
                                                            move_line.product_id.id),
                                                           ('lot_id', '=', move_line.lot_id.id)], limit=1)

            if quant:
                quant.write({'quantity': quant.quantity - move_line.qty_done})


class Production(models.Model):
    _inherit = 'mrp.production'

    def action_mrp_cancel(self):
        for rec in self:
            if rec.sudo().mapped('move_raw_ids'):
                rec.sudo().mapped('move_raw_ids').sudo().write(
                    {'state': 'cancel'})
                rec.sudo().mapped('move_raw_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'cancel'})
                rec.sudo().mapped('move_raw_ids')._sh_unreseve_qty()

                if rec.sudo().mapped('move_raw_ids').mapped('account_move_ids'):
                    accounting_ids = rec.sudo().mapped('move_raw_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

            if rec.sudo().mapped('workorder_ids'):
                rec.sudo().mapped('workorder_ids').write({'state': 'cancel'})

            if rec.sudo().mapped('move_byproduct_ids'):
                rec.sudo().mapped('move_byproduct_ids').sudo().write(
                    {'state': 'cancel'})
                rec.sudo().mapped('move_byproduct_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'cancel'})
                rec.sudo().mapped('move_byproduct_ids')._sh_unreseve_qty()

                if rec.sudo().mapped('move_byproduct_ids').mapped('account_move_ids'):
                    accounting_ids = rec.sudo().mapped('move_byproduct_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

            if rec.sudo().mapped('move_dest_ids'):
                rec.sudo().mapped('move_dest_ids').sudo().write(
                    {'state': 'cancel'})
                rec.sudo().mapped('move_dest_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'cancel'})
                rec.sudo().mapped('move_dest_ids')._sh_unreseve_qty()

                if rec.sudo().mapped('move_dest_ids').mapped('account_move_ids'):
                    accounting_ids = rec.sudo().mapped('move_dest_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

            if rec.sudo().mapped('move_finished_ids'):
                rec.sudo().mapped('move_finished_ids').sudo().write(
                    {'state': 'cancel'})
                rec.sudo().mapped('move_finished_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'cancel'})
                rec.sudo().mapped('move_finished_ids')._sh_unreseve_qty()

                if rec.sudo().mapped('move_finished_ids').mapped('account_move_ids'):
                    accounting_ids = rec.sudo().mapped('move_finished_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

            if rec.sudo().mapped('finished_move_line_ids'):
                rec.sudo().mapped('finished_move_line_ids').sudo().write(
                    {'state': 'cancel'})

            if rec.sudo().mapped('picking_ids'):
                rec.sudo().mapped('picking_ids').mapped(
                    'move_ids_without_package').sudo().write({'state': 'cancel'})
                rec.sudo().mapped('picking_ids').mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'cancel'})
                rec.sudo().mapped('picking_ids').mapped(
                    'move_ids_without_package')._sh_unreseve_qty()

                rec.sudo().mapped('picking_ids').write({'state': 'cancel'})

            rec.sudo().write({'state': 'cancel'})

    def action_mrp_cancel_draft(self):
        for rec in self:
            if rec.sudo().mapped('move_raw_ids'):
                rec.sudo().mapped('move_raw_ids').sudo().write(
                    {'state': 'draft'})
                rec.sudo().mapped('move_raw_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                rec.sudo().mapped('move_raw_ids')._sh_unreseve_qty()
                rec.sudo().mapped('move_raw_ids').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()

                if rec.sudo().mapped('move_raw_ids').mapped('account_move_ids'):
                    accounting_ids = rec.sudo().mapped('move_raw_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

            if rec.sudo().mapped('workorder_ids'):
                rec.sudo().mapped('workorder_ids').write({'state': 'ready'})

            if rec.sudo().mapped('move_byproduct_ids'):
                rec.sudo().mapped('move_byproduct_ids').sudo().write(
                    {'state': 'draft'})
                rec.sudo().mapped('move_byproduct_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                rec.sudo().mapped('move_byproduct_ids')._sh_unreseve_qty()
                rec.sudo().mapped('move_byproduct_ids').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()

                if rec.sudo().mapped('move_byproduct_ids').mapped('account_move_ids'):
                    accounting_ids = rec.sudo().mapped('move_byproduct_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

            if rec.sudo().mapped('move_dest_ids'):
                rec.sudo().mapped('move_dest_ids').sudo().write(
                    {'state': 'draft'})
                rec.sudo().mapped('move_dest_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                rec.sudo().mapped('move_dest_ids')._sh_unreseve_qty()
                rec.sudo().mapped('move_dest_ids').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()

                if rec.sudo().mapped('move_dest_ids').mapped('account_move_ids'):
                    accounting_ids = rec.sudo().mapped('move_dest_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

            if rec.sudo().mapped('move_finished_ids'):
                rec.sudo().mapped('move_finished_ids').sudo().write(
                    {'state': 'draft'})
                rec.sudo().mapped('move_finished_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                rec.sudo().mapped('move_finished_ids')._sh_unreseve_qty()
                rec.sudo().mapped('move_finished_ids').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()

                if rec.sudo().mapped('move_finished_ids').mapped('account_move_ids'):
                    accounting_ids = rec.sudo().mapped('move_finished_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

            if rec.sudo().mapped('finished_move_line_ids'):
                rec.sudo().mapped('finished_move_line_ids').sudo().write(
                    {'state': 'draft'})

            if rec.sudo().mapped('picking_ids'):
                rec.sudo().mapped('picking_ids').mapped(
                    'move_ids_without_package').sudo().write({'state': 'draft'})
                rec.sudo().mapped('picking_ids').mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                rec.sudo().mapped('picking_ids').mapped('move_ids_without_package').mapped('move_line_ids').write({'qty_done': 0.0})
                print('TEST 112233')
                rec.sudo().mapped('picking_ids').picking.mapped('move_lines')._action_cancel()
                rec.sudo().mapped('picking_ids').mapped(
                    'move_ids_without_package')._sh_unreseve_qty()
                rec.sudo().mapped('picking_ids').mapped('move_ids_without_package').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()
                rec.sudo().mapped('picking_ids').write({'state': 'draft'})

            rec.sudo().write({'state': 'draft'})

    def action_mrp_cancel_delete(self):
        for rec in self:
            if rec.sudo().mapped('move_raw_ids'):
                rec.sudo().mapped('move_raw_ids').sudo().write(
                    {'state': 'draft'})
                rec.sudo().mapped('move_raw_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                rec.sudo().mapped('move_raw_ids')._sh_unreseve_qty()

                if rec.sudo().mapped('move_raw_ids').mapped('account_move_ids'):
                    accounting_ids = rec.sudo().mapped('move_raw_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

                rec.sudo().mapped('move_raw_ids').mapped('move_line_ids').sudo().unlink()
                rec.sudo().mapped('move_raw_ids').sudo().unlink()
                rec.sudo().mapped('move_raw_ids').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()

            if rec.sudo().mapped('workorder_ids'):
                rec.sudo().mapped('workorder_ids').write({'state': 'ready'})

            if rec.sudo().mapped('move_byproduct_ids'):
                rec.sudo().mapped('move_byproduct_ids').sudo().write(
                    {'state': 'draft'})
                rec.sudo().mapped('move_byproduct_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                rec.sudo().mapped('move_byproduct_ids')._sh_unreseve_qty()

                if rec.sudo().mapped('move_byproduct_ids').mapped('account_move_ids'):
                    accounting_ids = rec.sudo().mapped('move_byproduct_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

                rec.sudo().mapped('move_byproduct_ids').mapped('move_line_ids').sudo().unlink()
                rec.sudo().mapped('move_byproduct_ids').sudo().unlink()
                rec.sudo().mapped('move_byproduct_ids').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()

            if rec.sudo().mapped('move_dest_ids'):
                rec.sudo().mapped('move_dest_ids').sudo().write(
                    {'state': 'draft'})
                rec.sudo().mapped('move_dest_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                rec.sudo().mapped('move_dest_ids')._sh_unreseve_qty()

                if rec.sudo().mapped('move_dest_ids').mapped('account_move_ids'):
                    accounting_ids = rec.sudo().mapped('move_dest_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

                rec.sudo().mapped('move_dest_ids').mapped('move_line_ids').sudo().unlink()
                rec.sudo().mapped('move_dest_ids').sudo().unlink()
                rec.sudo().mapped('move_dest_ids').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()

            if rec.sudo().mapped('move_finished_ids'):
                rec.sudo().mapped('move_finished_ids').sudo().write(
                    {'state': 'draft'})
                rec.sudo().mapped('move_finished_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                rec.sudo().mapped('move_finished_ids')._sh_unreseve_qty()

                if rec.sudo().mapped('move_finished_ids').mapped('account_move_ids'):
                    accounting_ids = rec.sudo().mapped('move_finished_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

                rec.sudo().mapped('move_finished_ids').mapped('move_line_ids').sudo().unlink()
                rec.sudo().mapped('move_finished_ids').sudo().unlink()
                rec.sudo().mapped('move_finished_ids').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()

            if rec.sudo().mapped('finished_move_line_ids'):
                rec.sudo().mapped('finished_move_line_ids').sudo().write(
                    {'state': 'draft'})
                rec.sudo().mapped('finished_move_line_ids').sudo().unlink()

            if rec.sudo().mapped('picking_ids'):
                rec.sudo().mapped('picking_ids').mapped(
                    'move_ids_without_package').sudo().write({'state': 'draft'})
                rec.sudo().mapped('picking_ids').mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                rec.sudo().mapped('picking_ids').mapped(
                    'move_ids_without_package')._sh_unreseve_qty()
                rec.sudo().mapped('picking_ids').mapped('move_ids_without_package').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()
                rec.sudo().mapped('picking_ids').write({'state': 'draft'})

            rec.sudo().write({'state': 'draft'})

            rec.sudo().unlink()

    def sh_cancel(self):

        if self.company_id.mrp_operation_type == 'cancel':
            if self.sudo().mapped('move_raw_ids'):
                self.sudo().mapped('move_raw_ids').sudo().write(
                    {'state': 'cancel'})
                self.sudo().mapped('move_raw_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'cancel'})
                self.sudo().mapped('move_raw_ids')._sh_unreseve_qty()

                if self.sudo().mapped('move_raw_ids').mapped('account_move_ids'):
                    accounting_ids = self.sudo().mapped('move_raw_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

            if self.sudo().mapped('workorder_ids'):
                self.sudo().mapped('workorder_ids').write({'state': 'cancel'})

            if self.sudo().mapped('move_byproduct_ids'):
                self.sudo().mapped('move_byproduct_ids').sudo().write(
                    {'state': 'cancel'})
                self.sudo().mapped('move_byproduct_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'cancel'})
                self.sudo().mapped('move_byproduct_ids')._sh_unreseve_qty()

                if self.sudo().mapped('move_byproduct_ids').mapped('account_move_ids'):
                    accounting_ids = self.sudo().mapped('move_byproduct_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

            if self.sudo().mapped('move_dest_ids'):
                self.sudo().mapped('move_dest_ids').sudo().write(
                    {'state': 'cancel'})
                self.sudo().mapped('move_dest_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'cancel'})
                self.sudo().mapped('move_dest_ids')._sh_unreseve_qty()

                if self.sudo().mapped('move_dest_ids').mapped('account_move_ids'):
                    accounting_ids = self.sudo().mapped('move_dest_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

            if self.sudo().mapped('move_finished_ids'):
                self.sudo().mapped('move_finished_ids').sudo().write(
                    {'state': 'cancel'})
                self.sudo().mapped('move_finished_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'cancel'})
                self.sudo().mapped('move_finished_ids')._sh_unreseve_qty()

                if self.sudo().mapped('move_finished_ids').mapped('account_move_ids'):
                    accounting_ids = self.sudo().mapped('move_finished_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

            if self.sudo().mapped('finished_move_line_ids'):
                self.sudo().mapped('finished_move_line_ids').sudo().write(
                    {'state': 'cancel'})

            if self.sudo().mapped('picking_ids'):
                self.sudo().mapped('picking_ids').mapped(
                    'move_ids_without_package').sudo().write({'state': 'cancel'})
                self.sudo().mapped('picking_ids').mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'cancel'})
                self.sudo().mapped('picking_ids').mapped('move_ids_without_package').mapped('move_line_ids').write(
                    {'qty_done': 0.0})
                self.sudo().mapped('picking_ids').mapped(
                    'move_ids_without_package')._sh_unreseve_qty()

                self.sudo().mapped('picking_ids').write({'state': 'cancel'})

            self.sudo().write({'state': 'cancel'})
        elif self.company_id.mrp_operation_type == 'cancel_draft':

            if self.sudo().mapped('move_raw_ids'):
                self.sudo().mapped('move_raw_ids').sudo().write(
                    {'state': 'draft'})
                self.sudo().mapped('move_raw_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                self.sudo().mapped('move_raw_ids')._sh_unreseve_qty()
                self.sudo().mapped('move_raw_ids').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()

                if self.sudo().mapped('move_raw_ids').mapped('account_move_ids'):
                    accounting_ids = self.sudo().mapped('move_raw_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

            if self.sudo().mapped('workorder_ids'):
                self.sudo().mapped('workorder_ids').write({'state': 'ready'})

            if self.sudo().mapped('move_byproduct_ids'):
                self.sudo().mapped('move_byproduct_ids').sudo().write(
                    {'state': 'draft'})
                self.sudo().mapped('move_byproduct_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                self.sudo().mapped('move_byproduct_ids')._sh_unreseve_qty()
                self.sudo().mapped('move_byproduct_ids').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()

                if self.sudo().mapped('move_byproduct_ids').mapped('account_move_ids'):
                    accounting_ids = self.sudo().mapped('move_byproduct_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

            if self.sudo().mapped('move_dest_ids'):
                self.sudo().mapped('move_dest_ids').sudo().write(
                    {'state': 'draft'})
                self.sudo().mapped('move_dest_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                self.sudo().mapped('move_dest_ids')._sh_unreseve_qty()
                self.sudo().mapped('move_dest_ids').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()

                if self.sudo().mapped('move_dest_ids').mapped('account_move_ids'):
                    accounting_ids = self.sudo().mapped('move_dest_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

            if self.sudo().mapped('move_finished_ids'):
                self.sudo().mapped('move_finished_ids').sudo().write(
                    {'state': 'draft'})
                self.sudo().mapped('move_finished_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                self.sudo().mapped('move_finished_ids')._sh_unreseve_qty()
                self.sudo().mapped('move_finished_ids').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()

                if self.sudo().mapped('move_finished_ids').mapped('account_move_ids'):
                    accounting_ids = self.sudo().mapped('move_finished_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

            if self.sudo().mapped('finished_move_line_ids'):
                self.sudo().mapped('finished_move_line_ids').sudo().write(
                    {'state': 'draft'})

            if self.sudo().mapped('picking_ids'):
                self.sudo().mapped('picking_ids').mapped(
                    'move_ids_without_package').sudo().write({'state': 'draft'})
                self.sudo().mapped('picking_ids').mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                self.sudo().mapped('picking_ids').mapped('move_ids_without_package').mapped('move_line_ids').write(
                    {'qty_done': 0.0})
                self.sudo().mapped('picking_ids').mapped(
                    'move_ids_without_package')._sh_unreseve_qty()
                self.sudo().mapped('picking_ids').mapped('move_ids_without_package').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()
                self.sudo().mapped('picking_ids').write({'state': 'draft'})

            self.sudo().write({'state': 'draft'})
        elif self.company_id.mrp_operation_type == 'cancel_delete':

            if self.sudo().mapped('move_raw_ids'):
                self.sudo().mapped('move_raw_ids').sudo().write(
                    {'state': 'draft'})
                self.sudo().mapped('move_raw_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                self.sudo().mapped('move_raw_ids')._sh_unreseve_qty()

                if self.sudo().mapped('move_raw_ids').mapped('account_move_ids'):
                    accounting_ids = self.sudo().mapped('move_raw_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

                self.sudo().mapped('move_raw_ids').mapped('move_line_ids').sudo().unlink()
                self.sudo().mapped('move_raw_ids').sudo().unlink()
                self.sudo().mapped('move_raw_ids').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()

            if self.sudo().mapped('workorder_ids'):
                self.sudo().mapped('workorder_ids').write({'state': 'ready'})

            if self.sudo().mapped('move_byproduct_ids'):
                self.sudo().mapped('move_byproduct_ids').sudo().write(
                    {'state': 'draft'})
                self.sudo().mapped('move_byproduct_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                self.sudo().mapped('move_byproduct_ids')._sh_unreseve_qty()

                if self.sudo().mapped('move_byproduct_ids').mapped('account_move_ids'):
                    accounting_ids = self.sudo().mapped('move_byproduct_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

                self.sudo().mapped('move_byproduct_ids').mapped('move_line_ids').sudo().unlink()
                self.sudo().mapped('move_byproduct_ids').sudo().unlink()
                self.sudo().mapped('move_byproduct_ids').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()

            if self.sudo().mapped('move_dest_ids'):
                self.sudo().mapped('move_dest_ids').sudo().write(
                    {'state': 'draft'})
                self.sudo().mapped('move_dest_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                self.sudo().mapped('move_dest_ids')._sh_unreseve_qty()

                if self.sudo().mapped('move_dest_ids').mapped('account_move_ids'):
                    accounting_ids = self.sudo().mapped('move_dest_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()

                self.sudo().mapped('move_dest_ids').mapped('move_line_ids').sudo().unlink()
                self.sudo().mapped('move_dest_ids').sudo().unlink()
                self.sudo().mapped('move_dest_ids').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()

            if self.sudo().mapped('move_finished_ids'):
                self.sudo().mapped('move_finished_ids').sudo().write(
                    {'state': 'draft'})
                self.sudo().mapped('move_finished_ids').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                self.sudo().mapped('move_finished_ids')._sh_unreseve_qty()

                if self.sudo().mapped('move_finished_ids').mapped('account_move_ids'):
                    accounting_ids = self.sudo().mapped('move_finished_ids').mapped('account_move_ids')
                    accounting_ids.sudo().write({'state': 'draft', 'name': '/'})
                    # accounting_ids.sudo().unlink()
                    accounting_ids.sudo().mapped('line_ids').sudo().write({'parent_state': 'draft'})
                    accounting_ids.sudo().mapped('line_ids').sudo().unlink()
                self.sudo().mapped('move_finished_ids').mapped('move_line_ids').sudo().unlink()
                self.sudo().mapped('move_finished_ids').sudo().unlink()
                self.sudo().mapped('move_finished_ids').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()

            if self.sudo().mapped('finished_move_line_ids'):
                self.sudo().mapped('finished_move_line_ids').sudo().write(
                    {'state': 'draft'})
                self.sudo().mapped('finished_move_line_ids').sudo().unlink()

            if self.sudo().mapped('picking_ids'):
                self.sudo().mapped('picking_ids').mapped(
                    'move_ids_without_package').sudo().write({'state': 'draft'})
                self.sudo().mapped('picking_ids').mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                self.sudo().mapped('picking_ids').mapped('move_ids_without_package').mapped('move_line_ids').write(
                    {'qty_done': 0.0})
                self.sudo().mapped('picking_ids').mapped(
                    'move_ids_without_package')._sh_unreseve_qty()
                self.sudo().mapped('picking_ids').mapped('move_ids_without_package').mapped(
                    'stock_valuation_layer_ids').sudo().unlink()
                self.sudo().mapped('picking_ids').write({'state': 'draft'})

            self.sudo().write({'state': 'draft'})

            self.sudo().unlink()
            return {
                'name': 'Manufacturing Orders',
                'type': 'ir.actions.act_window',
                'res_model': 'mrp.production',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'target': 'current',
            }
