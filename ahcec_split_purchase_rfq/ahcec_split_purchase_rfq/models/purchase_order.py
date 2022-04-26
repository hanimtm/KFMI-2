# -*- coding: utf-8 -*-
#################################################################################

from odoo import api,fields,models,_
from odoo.exceptions import ValidationError
import json


class PurchaseOrder(models.Model):
    _inherit ='purchase.order'

    # Define function to split purchase ordeline when we click on button
    def btn_split_rfq(self):
        for record in self: 
            if record.order_line:
                cnt = 0
                for rec in record.order_line:
                    if rec.split:
                        cnt += 1
                if cnt >= 1:
                    quotation_id = record.copy()
                    quotation_id.write({'origin':record.origin})
                    if quotation_id:
                        for line in quotation_id.order_line:
                            if not line.split:
                                line.unlink()
                            else:
                                line.split = False
                                line.purchase_origin = json.dumps([(quotation_id.origin, line.product_qty)])
                    for order_line in record.order_line:
                        if order_line.split:
                            order_line.unlink()
                else:
                    raise ValidationError(_('Please Select Order Line To Split'))
