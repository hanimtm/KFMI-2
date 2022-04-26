# -*- coding:utf-8 -*-
from collections import defaultdict
from odoo.tools import float_is_zero
from odoo import fields, models, api


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    bom_id = fields.Many2one('mrp.bom', string='BOM', copy=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
