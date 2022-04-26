# -*- coding:utf-8 -*-
from odoo import fields, models, api
import datetime
from collections import defaultdict


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    customer_warehouse_id = fields.Many2one('stock.warehouse', string='Customer Warehouse')
    customer_warehouse = fields.Char(string='Customer Warehouse')
    wbs = fields.Char(string='WBS')
    # Production Approval part
    state = fields.Selection(selection_add=[('approve', 'Production Approval'),('done', 'Done')])
    need_approval = fields.Boolean(related='location_dest_id.need_approval', string='Need Approval?')
    approval_date = fields.Datetime(string='Approval Date', copy=False)
    approval_user_id = fields.Many2one('res.users', string='Approved By', copy=False)
    show_production_approval = fields.Boolean(string='Show Approval', compute='set_show_approval')

    def action_approve(self):
        self.write({
            'state': 'assigned',
            'approval_date': datetime.datetime.now(),
            'approval_user_id': self.env.user.id
        })
        return True

    def action_assign(self):
        res = super().action_assign()
        if self.need_approval and not self.approval_date and not self.approval_user_id:
            self.write({
                'state': 'approve'
            })
        return res

    @api.onchange('state')
    def onchange_picking_state(self,):
        if self.state == 'approve':
            self.approval_date = fields.Datetime.now
            self.approval_user_id = self.env.user.id

    @api.depends('state')
    def set_show_approval(self):
        for picking in self:
            show = False
            if picking.state in ['assigned','approve'] and picking.need_approval:
                if not picking.approval_date and not picking.approval_user_id:
                    show = True
            picking.show_production_approval = show

    @api.depends('state')
    def _compute_show_validate(self):
        for picking in self:
            if not (picking.immediate_transfer) and picking.state == 'draft':
                picking.show_validate = False
            elif picking.state not in ('draft', 'waiting', 'confirmed', 'assigned'):
                picking.show_validate = False
            else:
                if picking.need_approval and not picking.approval_date and not picking.approval_user_id:
                    picking.show_validate = False
                else:
                    picking.show_validate = True

    def do_unreserve(self):
        res = super().do_unreserve()
        self.write({
            'approval_date': False,
            'approval_user_id': False
        })
        return res

    @api.depends('move_type', 'immediate_transfer', 'move_lines.state', 'move_lines.picking_id')
    def _compute_state(self):
        ''' State of a picking depends on the state of its related stock.move
        - Draft: only used for "planned pickings"
        - Waiting: if the picking is not ready to be sent so if
          - (a) no quantity could be reserved at all or if
          - (b) some quantities could be reserved and the shipping policy is "deliver all at once"
        - Waiting another move: if the picking is waiting for another move
        - Ready: if the picking is ready to be sent so if:
          - (a) all quantities are reserved or if
          - (b) some quantities could be reserved and the shipping policy is "as soon as possible"
        - Done: if the picking is done.
        - Cancelled: if the picking is cancelled
        '''
        # Overwrite and added 'approve' state
        picking_moves_state_map = defaultdict(dict)
        picking_move_lines = defaultdict(set)
        for move in self.env['stock.move'].search([('picking_id', 'in', self.ids)]):
            picking_id = move.picking_id
            move_state = move.state
            picking_moves_state_map[picking_id.id].update({
                'any_draft': picking_moves_state_map[picking_id.id].get('any_draft', False) or move_state == 'draft',
                'all_cancel': picking_moves_state_map[picking_id.id].get('all_cancel', True) and move_state == 'cancel',
                'all_cancel_done': picking_moves_state_map[picking_id.id].get('all_cancel_done', True) and move_state in ('cancel', 'done'),
            })
            picking_move_lines[picking_id.id].add(move.id)
        for picking in self:
            picking_id = (picking.ids and picking.ids[0]) or picking.id
            if not picking_moves_state_map[picking_id]:
                picking.state = 'draft'
            elif picking_moves_state_map[picking_id]['any_draft']:
                picking.state = 'draft'
            elif picking_moves_state_map[picking_id]['all_cancel']:
                picking.state = 'cancel'
            elif picking_moves_state_map[picking_id]['all_cancel_done']:
                picking.state = 'done'
            else:
                relevant_move_state = self.env['stock.move'].browse(picking_move_lines[picking_id])._get_relevant_state_among_moves()
                if picking.immediate_transfer and relevant_move_state not in ('draft', 'cancel', 'done'):
                    if picking.need_approval and not picking.approval_date and not picking.approval_user_id:
                        picking.state = 'approve'
                    else:
                        picking.state = 'assigned'
                elif relevant_move_state == 'partially_available':
                    if picking.need_approval and not picking.approval_date and not picking.approval_user_id:
                        picking.state = 'approve'
                    else:
                        picking.state = 'assigned'
                else:
                    if picking.need_approval and not picking.approval_date and not picking.approval_user_id:
                        picking.state = 'approve'
                    else:
                        picking.state = relevant_move_state

class StockLocation(models.Model):
    _inherit = 'stock.location'

    need_approval = fields.Boolean(string='Need Approval?')


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    def compute_ready_pre_approve_count(self):
        domains = {
            'count_picking_ready_pre_approve': [
                ('state', 'in', ['assigned', 'approve'])],
        }
        for field in domains:
            data = self.env['stock.picking'].read_group(domains[field] +
                [('state', 'not in', ('done', 'cancel')), ('picking_type_id', 'in', self.ids)],
                ['picking_type_id'], ['picking_type_id'])
            count = {
                x['picking_type_id'][0]: x['picking_type_id_count']
                for x in data if x['picking_type_id']
            }
            for record in self:
                record[field] = count.get(record.id, 0)


    count_picking_ready_pre_approve = fields.Integer(
        compute='compute_ready_pre_approve_count')

    def get_action_picking_tree_production_approve(self):
        return self._get_action('khalifa_customizations.action_picking_tree_ready_and_approve')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
