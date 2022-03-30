# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _rec_name = 'display_name'

    arabic = fields.Char(
        'Arabic Name'
    )
    district = fields.Char(
        'District'
    )
    cr_number = fields.Char(
        'CR Number'
    )
    customer_no = fields.Char(
        'Customer No.'
    )
    location = fields.Char(
        'Location.'
    )
    additional_no = fields.Char(
        'Additional No.'
    )

    def name_get(self):
        if self._context.get('partner_category_display') == 'short':
            return super(res_partner, self).name_get()

        res = []
        for category in self:
            names = []
            current = category
            while current:
                if self.env.user.lang == 'en_US' or not current.arabic:
                    names.append(current.name)
                else:
                    names.append(current.arabic)
                current = current.parent_id
            res.append((category.id, ' / '.join(reversed(names))))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            print(name)
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = ['|',('name', operator, name),('arabic', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)