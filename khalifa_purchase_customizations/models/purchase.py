# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    active = fields.Boolean("Active", default=True)

    def toggle_active(self):
        if not self.active:
            self.active = True

    def toggle_archive(self):
        if self.active:
            self.active = False

