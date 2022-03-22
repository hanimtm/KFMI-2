from odoo import api, fields, models, exceptions, _
from odoo.tools.float_utils import float_round, float_compare, float_is_zero
from odoo.addons.mrp.models.stock_move import StockMove
from odoo.addons.mrp.models.mrp_workorder import MrpWorkorder
from odoo.exceptions import UserError


class Mrp_Workorder(models.Model):
    _inherit = 'mrp.workorder'

    def write(self, values):
        if 'production_id' in values:
            raise UserError(_('You cannot link this work order to another manufacturing order.'))
        if 'workcenter_id' in values:
            for workorder in self:
                if workorder.workcenter_id.id != values['workcenter_id']:
                    if workorder.state in ('progress', 'done', 'cancel'):
                        raise UserError(_('You cannot change the workcenter of a work order that is in progress or done.'))
                    workorder.leave_id.resource_id = self.env['mrp.workcenter'].browse(values['workcenter_id']).resource_id
        if 'date_planned_start' in values or 'date_planned_finished' in values:
            for workorder in self:
                start_date = fields.Datetime.to_datetime(values.get('date_planned_start')) or workorder.date_planned_start
                end_date = fields.Datetime.to_datetime(values.get('date_planned_finished')) or workorder.date_planned_finished
                if start_date and end_date and start_date > end_date:
                    raise UserError(_('The planned end date of the work order cannot be prior to the planned start date, please correct this to save the work order.'))
                if workorder == workorder.production_id.workorder_ids[0] and ('date_planned_start' in values) and values['date_planned_start']:
                    workorder.production_id.with_context(force_date=True).write({
                        'date_planned_start': fields.Datetime.to_datetime(values['date_planned_start'])
                    })
                if workorder == workorder.production_id.workorder_ids[-1] and 'date_planned_finished' in values and values['date_planned_finished']:
                    workorder.production_id.with_context(force_date=True).write({
                        'date_planned_finished': fields.Datetime.to_datetime(values['date_planned_finished'])
                    })
        return super(MrpWorkorder, self).write(values)

    MrpWorkorder.write = write


class Stock_Move(models.Model):
    _inherit = 'stock.move'

    def _action_cancel(self):
        return super(StockMove, self)._action_cancel()

    StockMove._action_cancel = _action_cancel


class ManufacturingOrder(models.Model):
    _inherit = "mrp.production"

    def action_cancel(self):
        quant_obj = self.env['stock.quant']
        account_move_obj = self.env['account.move']
        stk_mv_obj = self.env['stock.move']
        for order in self:
            
            if order.company_id.cancel_inventory_move_for_mo:
                moves = stk_mv_obj.search(['|',('production_id', '=', order.id),('raw_material_production_id','=',order.id)])

                for move in moves:
                    if move.state == 'cancel':
                        continue
                    if move.state == "done" and move.product_id.type == "product":
                        for move_line in move.move_line_ids:
                            quantity = move_line.product_uom_id._compute_quantity(move_line.qty_done, move_line.product_id.uom_id)
                            quant_obj._update_available_quantity(move_line.product_id, move_line.location_id, quantity,move_line.lot_id)
                            quant_obj._update_available_quantity(move_line.product_id, move_line.location_dest_id, quantity * -1,move_line.lot_id)
                    if move.procure_method == 'make_to_order' and not move.move_orig_ids:
                        move.state = 'waiting'
                    elif move.move_orig_ids and not all(orig.state in ('done', 'cancel') for orig in move.move_orig_ids):
                        move.state = 'waiting'
                    else:
                        if move.state != 'confirmed':
                            move.state = 'confirmed'
                    siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
                    if move.propagate_cancel:
                        if all(state == 'cancel' for state in siblings_states):
                            move.move_dest_ids._action_cancel()
                    else:
                        if all(state in ('done', 'cancel') for state in siblings_states):
                            move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                        move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)], 'move_orig_ids': [(5, 0, 0)]})
                    move.write({'state': 'cancel'})
                    account_moves = account_move_obj.search([('stock_move_id', '=', move.id)])
                    valuation = move.stock_valuation_layer_ids
                    valuation and valuation.sudo().unlink()
                    if account_moves:
                        for account_move in account_moves:
                            # account_move.quantity_done = 0.0
                            account_move.button_cancel()
                            account_move.with_context(force_delete=True).unlink()

            if order.company_id.cancel_work_order_for_mo:
                order.workorder_ids.action_cancel()
                    
        res = super(ManufacturingOrder, self).action_cancel()
        return res
