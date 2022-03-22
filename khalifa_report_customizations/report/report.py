# -*- coding: utf-8 -*-
import datetime
from odoo import api, models, _


class ReportGoodsDeliveryNote(models.AbstractModel):
    _name = 'report.khalifa_report_customizations.report_goods_delivery_note'
    _description = 'Goods Delivery Note'

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % (self.type_name, self.name)

    @api.model
    def _get_report_values(self, docids, data=None):
        records = []
        for doc in docids:
            records.append(self.env['stock.picking'].browse(doc))
        report = self.env['ir.actions.report']._get_report_from_name('khalifa_report_customizations.report_goods_delivery_note')
        # records = self.env['accounting.assert.test'].browse(self.ids)
        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': records,
            'data': records,

        }
