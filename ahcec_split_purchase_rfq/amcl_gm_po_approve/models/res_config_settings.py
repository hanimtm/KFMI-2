# -*- coding:utf-8 -*-
from odoo import fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gm_po_approval = fields.Boolean(string='Purchase GM Approval', default=lambda self: self.env.company.gm_po_double_approval == 'two_step')
    gm_po_double_approval = fields.Selection(related='company_id.gm_po_double_approval', string="GM Levels of Approvals *", readonly=False)
    gm_po_double_approval_amount = fields.Monetary(related='company_id.gm_po_double_approval_amount', string="Min Amount", currency_field='company_currency_id', readonly=False)

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.gm_po_double_approval = 'two_step' if self.gm_po_approval else 'one_step'
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
