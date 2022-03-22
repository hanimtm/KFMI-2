# -*- coding:utf-8 -*-
from odoo import fields, models, _


class DiscountConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    sales_discount_account_id = fields.Many2one('account.account',
                                                string="Sales Discount Account")
    purchase_discount_account_id = fields.Many2one('account.account',
                                                   string="Purchase Discount Account")

    def get_values(self):
        res = super(DiscountConfigSetting, self).get_values()
        res.update({'sales_discount_account_id': 
                            int(self.env['ir.config_parameter'].sudo().get_param('sales_discount_account_id')) or False,
                    'purchase_discount_account_id': 
                            int(self.env['ir.config_parameter'].sudo().get_param('purchase_discount_account_id'))or False})
        return res

    def set_values(self):
        res = super(DiscountConfigSetting, self).set_values()
        if self.sales_discount_account_id:
            self.env['ir.config_parameter'].sudo().set_param('sales_discount_account_id',
                                                                 self.sales_discount_account_id.id or False)
        if self.purchase_discount_account_id:
            self.env['ir.config_parameter'].sudo().set_param('purchase_discount_account_id',
                                                                self.purchase_discount_account_id.id or False)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
