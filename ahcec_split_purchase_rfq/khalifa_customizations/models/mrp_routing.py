# -*- coding:utf-8 -*-
from odoo import fields, models, api, _


class MrpRouting(models.Model):
    _name = 'mrp.routing'
    _description = 'Routing'

    name = fields.Char(string='Routing Name', required=True)
    bom_id = fields.Many2one('mrp.bom', string='BOM')
    active = fields.Boolean(
        string='Active', default=True,
        help="If the active field is set to False, it will allow you to hide the routing without removing it.")
    code = fields.Char(
        string='Reference',
        copy=False, default=lambda self: _('New'), readonly=True)
    note = fields.Text(string='Description')
    operation_ids = fields.One2many(
        'custom.routing.workcenter', 'routing_id', string='Operations', copy=True)
    location_id = fields.Many2one(
        'stock.location', string='Raw Materials Location',
        help="Keep empty if you produce at the location where you find the raw materials. "
             "Set a location if you produce at a fixed location. This can be a partner location "
             "if you subcontract the manufacturing operations.")
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        if 'code' not in vals or vals['code'] == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('mrp.routing') or _('New')
        return super(MrpRouting, self).create(vals)


class CustomRoutingWorkcenter(models.Model):
    _name = 'custom.routing.workcenter'
    _description = 'Custom Routing Workcenter'

    routing_id = fields.Many2one('mrp.routing', string='Routing')
    name = fields.Char(string='Operation', required=True)
    active = fields.Boolean(default=True)
    quality_point_count = fields.Float(string='Steps')
    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Center', required=True)
    sequence = fields.Integer(
        string='Sequence', default=100,
        help="Gives the sequence order when displaying a list of routing Work Centers.")
    # bom_id = fields.Many2one(
    #     'mrp.bom', 'Bill of Material',
    #     index=True, ondelete='cascade', required=True, check_company=True,
    #     help="The Bill of Material this operation is linked to")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    worksheet_type = fields.Selection([
        ('pdf', 'PDF'), ('google_slide', 'Google Slide'), ('text', 'Text')],
        string="Work Sheet", default="text",
        help="Defines if you want to use a PDF or a Google Slide as work sheet."
    )
    note = fields.Html(string='Description', help="Text worksheet description")
    worksheet = fields.Binary(string='PDF')
    worksheet_google_slide = fields.Char(string='Google Slide', help="Paste the url of your Google Slide. Make sure the access to the document is public.")
    time_mode = fields.Selection([
        ('auto', 'Compute based on tracked time'),
        ('manual', 'Set duration manually')], string='Duration Computation',
        default='manual')
    time_mode_batch = fields.Integer(string='Based on', default=10)
    time_computed_on = fields.Char(string='Computed on last', compute='_compute_time_computed_on')
    time_cycle_manual = fields.Float(
        string='Manual Duration', default=60,
        help="Time in minutes:"
        "- In manual mode, time used"
        "- In automatic mode, supposed first time when there aren't any work orders yet")
    time_cycle = fields.Float(string='Duration', compute="_compute_time_cycle")
    workorder_count = fields.Integer(string="# Work Orders", compute="_compute_workorder_count")
    # workorder_ids = fields.One2many('mrp.workorder', 'operation_id', string="Work Orders")
    # possible_bom_product_template_attribute_value_ids = fields.Many2many(related='bom_id.possible_product_template_attribute_value_ids')
    # bom_product_template_attribute_value_ids = fields.Many2many(
    #     'product.template.attribute.value', string="Apply on Variants", ondelete='restrict',
    #     domain="[('id', 'in', possible_bom_product_template_attribute_value_ids)]",
    #     help="BOM Product Variants needed to apply this line.")

    @api.depends('time_mode', 'time_mode_batch')
    def _compute_time_computed_on(self):
        for operation in self:
            operation.time_computed_on = _('%i work orders') % operation.time_mode_batch if operation.time_mode != 'manual' else False

    @api.depends('time_cycle_manual', 'time_mode')# , 'workorder_ids'
    def _compute_time_cycle(self):
        manual_ops = self.filtered(lambda operation: operation.time_mode == 'manual')
        for operation in manual_ops:
            operation.time_cycle = operation.time_cycle_manual
        for operation in self - manual_ops:
            data = self.env['mrp.workorder'].search([
                ('operation_id', '=', operation.id),
                ('qty_produced', '>', 0),
                ('state', '=', 'done')],
                limit=operation.time_mode_batch,
                order="date_finished desc")
            # To compute the time_cycle, we can take the total duration of previous operations
            # but for the quantity, we will take in consideration the qty_produced like if the capacity was 1.
            # So producing 50 in 00:10 with capacity 2, for the time_cycle, we assume it is 25 in 00:10
            # When recomputing the expected duration, the capacity is used again to divide the qty to produce
            # so that if we need 50 with capacity 2, it will compute the expected of 25 which is 00:10
            total_duration = 0  # Can be 0 since it's not an invalid duration for BoM
            cycle_number = 0  # Never 0 unless infinite item['workcenter_id'].capacity
            for item in data:
                total_duration += item['duration']
                cycle_number += tools.float_round((item['qty_produced'] / item['workcenter_id'].capacity or 1.0), precision_digits=0, rounding_method='UP')
            if cycle_number:
                operation.time_cycle = total_duration / cycle_number
            else:
                operation.time_cycle = operation.time_cycle_manual

    def _compute_workorder_count(self):
        data = self.env['mrp.workorder'].read_group([
            ('operation_id', 'in', self.ids),
            ('state', '=', 'done')], ['operation_id'], ['operation_id'])
        count_data = dict((item['operation_id'][0], item['operation_id_count']) for item in data)
        for operation in self:
            operation.workorder_count = count_data.get(operation.id, 0)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
