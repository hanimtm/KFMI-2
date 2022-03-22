# -*- coding:utf-8 -*-
from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def name_search(self, name='', args=[], operator='ilike', limit=100):
        if self._context.get('filter_by_design'):
            design_user = self.env.ref('khalifa_customizations.design_user').id
            design_manager = self.env.ref('khalifa_customizations.design_manager').id
            args += [('groups_id','in',[design_user, design_manager])]
        res = super().name_search(name, args, operator, limit)
        return res


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def set_customer_location(self):
        partner_ids = self.env['res.partner'].search([('customer_rank','>',0)])
        for each in partner_ids:
            each.write({
                'property_stock_customer': 5
                })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
