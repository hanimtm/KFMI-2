# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    show_warning_alert = fields.Boolean('Show Alert', compute='_compute_show_warning_alert', )

    @api.depends('bom_line_ids', 'product_qty')
    def _compute_show_warning_alert(self):
        for bom in self:
            bom.show_warning_alert = False
            mo = self.env['mrp.production'].search(
                [('bom_id', '=', bom.id), ('state', '=', ('draft', 'confirmed', 'progress'))])
            if mo:
                bom.show_warning_alert = True
