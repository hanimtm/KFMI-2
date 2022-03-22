# -*- coding: utf-8 -*-

import json

from odoo import api, models, _
from odoo.tools import float_round


class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    @api.model
    def _get_report_data(self, bom_id, searchQty=0, searchVariant=False):
        res = super(ReportBomStructure, self)._get_report_data(
            bom_id, searchQty=searchQty, searchVariant=searchVariant)
        res.update({
            'show_bom_cost': self.env.user.user_has_groups(
                'amcl_hide_bom_cost.group_show_bom_cost'),
        })
        return res

    @api.model
    def get_html(self, bom_id=False, searchQty=1, searchVariant=False):
        res = self._get_report_data(
            bom_id=bom_id, searchQty=searchQty, searchVariant=searchVariant)
        res['lines']['report_type'] = 'html'
        res['lines']['report_structure'] = 'all'
        res['lines']['show_bom_cost'] = self.env.user.user_has_groups(
            'amcl_hide_bom_cost.group_show_bom_cost')
        res['lines']['has_attachments'] = res['lines']['attachments'] or any(
            component['attachments'] for component in res['lines'][
                'components'])
        res['lines'] = self.env.ref('mrp.report_mrp_bom')._render({
            'data': res['lines']})
        return res

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        for bom_id in docids:
            bom = self.env['mrp.bom'].browse(bom_id)
            variant = data.get('variant')
            candidates = variant and self.env['product.product'].browse(variant) or bom.product_id or bom.product_tmpl_id.product_variant_ids
            quantity = float(data.get('quantity', bom.product_qty))
            for product_variant_id in candidates.ids:
                if data and data.get('childs'):
                    doc = self._get_pdf_line(bom_id, product_id=product_variant_id, qty=quantity, child_bom_ids=set(json.loads(data.get('childs'))))
                else:
                    doc = self._get_pdf_line(bom_id, product_id=product_variant_id, qty=quantity, unfolded=True)
                doc['report_type'] = 'pdf'
                doc['report_structure'] = data and data.get('report_type') or 'all'
                doc['show_bom_cost'] = self.env.user.user_has_groups(
                    'amcl_hide_bom_cost.group_show_bom_cost')
                docs.append(doc)
            if not candidates:
                if data and data.get('childs'):
                    doc = self._get_pdf_line(bom_id, qty=quantity, child_bom_ids=set(json.loads(data.get('childs'))))
                else:
                    doc = self._get_pdf_line(bom_id, qty=quantity, unfolded=True)
                doc['report_type'] = 'pdf'
                doc['report_structure'] = data and data.get('report_type') or 'all'
                doc['show_bom_cost'] = self.env.user.user_has_groups(
                    'amcl_hide_bom_cost.group_show_bom_cost')
                docs.append(doc)
        return {
            'doc_ids': docids,
            'doc_model': 'mrp.bom',
            'docs': docs,
        }
