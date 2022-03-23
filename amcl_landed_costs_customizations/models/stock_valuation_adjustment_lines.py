from odoo import api, fields, models


class AdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'


    @api.depends('former_cost', 'quantity')
    def compute_unit_former_cost(self):
        for rec in self:
            unit_former_cost = 0
            if rec.former_cost and rec.quantity:
                unit_former_cost = rec.former_cost / rec.quantity
            rec.unit_former_cost = unit_former_cost

    @api.depends('additional_landed_cost', 'quantity')
    def compute_unit_additional_landed_cost(self):
        for rec in self:
            unit_additional_landed_cost = 0
            if rec.additional_landed_cost and rec.quantity:
                unit_additional_landed_cost = rec.additional_landed_cost / rec.quantity
            rec.unit_additional_landed_cost = unit_additional_landed_cost

    @api.depends('final_cost', 'quantity')
    def compute_unit_final_cost(self):
        for rec in self:
            unit_final_cost = 0
            if rec.final_cost and rec.quantity:
                unit_final_cost = rec.final_cost / rec.quantity
            rec.unit_final_cost = unit_final_cost

    unit_former_cost = fields.Monetary(
        'Unit Original Value', compute=compute_unit_former_cost, store=True)

    unit_additional_landed_cost = fields.Monetary(
        'Unit Additional Landed Cost', compute=compute_unit_additional_landed_cost, store=True)

    unit_final_cost = fields.Monetary(
        'Unit New Value', compute='compute_unit_final_cost',
        store=True)