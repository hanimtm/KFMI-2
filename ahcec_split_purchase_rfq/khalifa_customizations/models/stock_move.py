# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    sec_wh_id = fields.Many2one('sec.wh', related='sale_line_id.sec_wh_id',
                                string='SEC WH')
    line_no = fields.Char(string="Line No", related='sale_line_id.line_no')
