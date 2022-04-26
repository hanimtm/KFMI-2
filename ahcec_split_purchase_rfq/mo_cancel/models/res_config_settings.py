# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    cancel_inventory_move_for_mo = fields.Boolean(string="Cancel Inventory Moves?")
    cancel_work_order_for_mo = fields.Boolean(string='Cancel Work Orders?')

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            cancel_inventory_move_for_mo=self.env.user.company_id.cancel_inventory_move_for_mo ,
            cancel_work_order_for_mo=self.env.user.company_id.cancel_work_order_for_mo
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        company_id=self.env.user.company_id
        company_id.cancel_work_order_for_mo = self.cancel_work_order_for_mo
        company_id.cancel_inventory_move_for_mo = self.cancel_inventory_move_for_mo
