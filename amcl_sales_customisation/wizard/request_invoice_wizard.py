# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class RequestInvoiceWizard(models.Model):
    _name = 'request.invoice.wizard'
    _description = 'Request Invoice Wizard'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    requester = fields.Many2one('res.users',  related='sale_order_id.user_id', string='Requester')
    invoice_details = fields.Char(string='Invoice Details')
    supporting_document = fields.Binary(string='Supporting Document')

