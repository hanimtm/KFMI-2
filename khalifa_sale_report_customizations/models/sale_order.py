# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    attention = fields.Char("Attention", required=True)
    delivery_period = fields.Char("Delivery Period", required=True)
    incoterm_id = fields.Many2one('account.incoterms', 'Mode of Delivery',
                                  required=True,
                                  help="International Commercial Terms are a series of predefined commercial terms used in international transactions.")
    rfq_attachment_name = fields.Char('RFQ Attachment Name')
    rfq_attachment = fields.Binary('RFQ Attachment')
    def _get_vat_text(self):
        vat = ''
        arab = ''
        for tax in self.mapped('order_line.tax_id'):
            vat += str(tax.amount) + '%,'
            # arab += str(tax.amount_in_arabic) + '%,'
        # self.vat_text = vat[:-1]
        # self.vat_arabic_text = arab[:-1]
        return vat[:-1]
