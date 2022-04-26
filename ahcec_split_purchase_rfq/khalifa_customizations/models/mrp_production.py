# -*- coding:utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import fields, models, api, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    routing_id = fields.Many2one('mrp.routing', string='Routing', compute='set_routing')
    partner_id = fields.Many2one('res.partner', string='Client Name')
    client_name = fields.Char(string='Client Name', compute='set_client', store=True)
    client_order_ref = fields.Char(string='Customer Reference')
    drawing = fields.Char(related='bom_id.drawing', string='Drawing')
    label = fields.Char(related='bom_id.label', string='Label')
    sec_wh_id = fields.Many2one('sec.wh', related='bom_id.sec_wh_id',
                                string='SEC WH')
    line_no = fields.Char(string="Line No", related='bom_id.line_no')

    @api.depends('origin')
    def set_client(self):
        for each in self:
            if each.origin:
                sale_order_id = self.env['sale.order'].search([('name','=',each.origin)])
                if sale_order_id:
                    each.client_name = sale_order_id.partner_id.name
                    each.client_order_ref = sale_order_id.client_order_ref

    @api.depends('bom_id')
    def set_routing(self):
        routing_id = False
        if self.bom_id and self.bom_id.id:
            routing_id = self.bom_id.routing_id.id
        self.routing_id = routing_id

    def unlink(self):
        if any(production.state not in ['draft', 'cancel'] for production in self):
            raise ValidationError(_('Cannot delete a manufacturing order not in draft or cancel state'))
        return super().unlink()

    def action_confirm(self):
        if self._context.get('from_saleorder', False):
            return True
        res = super().action_confirm()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
