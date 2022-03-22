# -*- coding: utf-8 -*-
import json
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    procurement_manager = fields.Char("Procurement Manager")

    def get_total_with_tax(self):
        total_json = json.loads(self.tax_totals_json)
        if self.currency_id.position == 'after':
            total_amount = total_json.get(
                'formatted_amount_total', '0.0 ').split(' ')[0]
        else:
            total_amount = total_json.get(
                'formatted_amount_total', '0.0 ').split(' ')[1]
        print(total_amount)
        total_float_value = float(total_amount.replace(',',''))
        return total_float_value

    def get_tax_amount(self):
        total_json = json.loads(self.tax_totals_json)
        if total_json.get('groups_by_subtotal'):
            total_tax_amount = total_json.get('groups_by_subtotal').get(
            'Untaxed Amount')[0].get('tax_group_amount')
        else:
            total_tax_amount = 0
        return total_tax_amount
