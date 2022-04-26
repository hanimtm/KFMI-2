# -*- coding: utf-8 -*-
from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    gm_po_double_approval = fields.Selection([
        ('one_step', 'Confirm purchase orders in one step'),
        ('two_step', 'Get 2 levels of approvals to confirm a purchase order')
        ], string="Levels of Approvals", default='one_step')
    gm_po_double_approval_amount = fields.Monetary(string='GM Double Validation Amount', default=5000)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
