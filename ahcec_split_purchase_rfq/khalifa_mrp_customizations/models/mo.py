# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    hide_mark_as_done = fields.Boolean('Hide Mark as done', compute='_compute_hide_mark_as_done', )

    @api.depends('move_raw_ids')
    def _compute_hide_mark_as_done(self):
        qty = sum(self.move_raw_ids.mapped('quantity_remaining'))
        if qty != 0 and self.state not in ('draft', 'cancel','done'):
            self.hide_mark_as_done = False
        else:
            self.hide_mark_as_done = True
