# -*- coding: utf-8 -*-
import json
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    po_no = fields.Char("PO No.")