# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

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

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            print(name)
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = ['|',('name', operator, name),('arabic', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)