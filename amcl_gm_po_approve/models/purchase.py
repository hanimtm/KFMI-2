# -*- coding:utf-8 -*-
from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    date_gm_approve = fields.Datetime(string='GM Approved Date')
    state = fields.Selection(selection_add=[('to approve','Approve By PM'), ('to_gm_approve','To GM Approve'), ('purchase','Purchase Order')])

    def gm_approval_allowed(self):
        """Returns whether the order qualifies to be approved by the current user"""
        # If the user is general manager then it will approve.
        self.ensure_one()
        result = (
            self.company_id.gm_po_double_approval == 'one_step'
            or (self.company_id.gm_po_double_approval == 'two_step'
                and self.amount_total <= self.env.company.currency_id._convert(
                    self.company_id.gm_po_double_approval_amount, self.currency_id, self.company_id,
                    self.date_order or fields.Date.today()))
            or self.user_has_groups('amcl_gm_po_approve.group_general_manager'))
        return result

    def action_gm_approve(self):
        # Approve the purchase and change state to 'purchase(Purchase Order) and add date'
        self = self.filtered(lambda order: order.gm_approval_allowed())
        self.write({'state': 'purchase', 'date_gm_approve': fields.Datetime.now()})
        self.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
        self._create_picking()
        return {}
    
    def button_approve(self, force=False):
        # Once system checkes for purchase admin approval then we will check for GM(general MAnager) approval
        res = super().button_approve()
        if self.gm_approval_allowed():
            self.action_gm_approve()
        else:
            self.write({'state': 'to_gm_approve'})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
