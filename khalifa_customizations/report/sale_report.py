# -*- coding:utf-8 -*-
from odoo import models, api
from odoo.exceptions import ValidationError


class SaleReport(models.AbstractModel):
    _name = 'report.sale.report_saleorder'
    _description = 'Sale Order Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        acc_advisor = self.env.user.has_group('account.group_account_manager')
        admin = self.env.user.has_group('base.group_erp_manager')
        if not (acc_advisor or admin):
            self.validate_customer(docs)
        return {
              'doc_ids': docids,
              'doc_model': 'sale.order',
              'docs': docs,
              'data': data,
        }

    @api.model
    def validate_customer(self, docs):
        raise_warning = False
        for order_id in docs:
            query = """
                SELECT id
                FROM account_move
                WHERE invoice_date < current_date - interval '90' day
                AND move_type = 'out_invoice'
                AND payment_state IN ('not_paid','partial')
                AND partner_id = %s;
            """%(order_id.partner_id.id)
            self._cr.execute(query)
            result = self._cr.dictfetchall()
            if result:
                raise_warning = True
                break
        if raise_warning:
            raise ValidationError("Unpaid invoice(s) exist for this customer before 90 days.")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
