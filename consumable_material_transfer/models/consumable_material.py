# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError, UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class ConsumableMaterialTransfer(models.Model):
    _name = "consumable.material.transfer"
    _description = "Consumable Material Transfer"
    _inherit = ['mail.thread']

    name = fields.Char(string="Name", required=True, copy=False, default='New', readonly=True)
    company_id = fields.Many2one('res.company', string="Company",
        default=lambda self: self.env.user.company_id, required=True)
    source_location_id = fields.Many2one('stock.location', string="From", required=True)
    to_location_id = fields.Many2one('stock.analytic.location', string="To", required=True)
    destination_location_id = fields.Many2one(
        related='to_location_id.location_id', string="Destination Location", store=True)
    user_id = fields.Many2one('res.users', string="Responsible Person")
    reason = fields.Text(string="Reason For Transfer")
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('done', 'Transferred'), ('cancelled', 'Cancelled')], string="Status",
        default='draft', tracking=True)
    transferred_date = fields.Date(string="Transferred Date")
    received_user_id = fields.Many2one(
        'res.users', 'Received By', readonly=True)
    line_ids = fields.One2many(
        'consumable.material.line', 'consumable_id', string='Transfer Lines')
    requested_by = fields.Many2one('hr.employee', 'Requested By')

    @api.onchange('to_location_id')
    def _onchange_to_location_id(self):
        if self.to_location_id:
            if not self.to_location_id.analytic_account_id or not self.to_location_id.location_id:
                raise ValidationError("Please add the Analytic account or Location to To location")

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('consumable.material')
        vals['name'] = name
        return super(ConsumableMaterialTransfer, self).create(vals)

    def unlink(self):
        for transfer in self:
            if transfer.state not in ['draft', 'cancelled']:
                raise ValidationError("Only delete in draft or cancelled state")
        return super(ConsumableMaterialTransfer, self).unlink()

    def act_transfer(self):
        self.state = 'done'
        self.transferred_date = datetime.today()

    def act_cancel_manager(self):
        self.state = 'cancelled'

    def act_reset_draft(self):
        self.state = 'draft'


class ConsumableMaterialLine(models.Model):
    _name = 'consumable.material.line'
    _description = 'Consumable Material Line'

    @api.onchange('product_id')
    def onchange_product_id(self):
        """
        :return:
        """
        if self.product_id:
            self.product_uom = self.product_id.uom_id and self.product_id.uom_id.id

    product_id = fields.Many2one(
        'product.product', string='Product', check_company=True,
        domain="[('type', 'in', ['consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        index=True, required=True)
    sequence = fields.Integer('Sequence', default=10)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,
        index=True, required=True)
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template', related='product_id.product_tmpl_id', readonly=False)
    consumable_id = fields.Many2one(
        'consumable.material.transfer', 'Consumable Material', index=True, check_company=True)
    state = fields.Selection(
        related='consumable_id.state', string='State', store=True)
    done_qty = fields.Float('Done Qty', default=1)
