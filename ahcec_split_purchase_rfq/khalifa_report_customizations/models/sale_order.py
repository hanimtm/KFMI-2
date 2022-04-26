# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_print_goods_do_note(self):
        """
        :return:
        """
        if self.picking_ids:
            return self.env.ref('khalifa_report_customizations.report_goods_delivery_note_report').report_action(
                self.picking_ids.ids)
