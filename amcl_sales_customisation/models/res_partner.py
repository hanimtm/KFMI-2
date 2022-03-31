# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sales_type_id = fields.Many2one('sale.type', required=True, string='Sales Type')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', '|', '|', '|', ('name', operator, name),
                      ('mobile', operator, name), ('email', operator, name), ('phone', operator, name),
                      ('ref', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    def name_get(self):
        if self._context.get("only_mobile"):
            res = []
            for record in self:
                mobile = record.mobile or ""
                name = mobile
                res.append((record.id, name))
            return res
        if self._context.get("only_email"):
            res = []
            for record in self:
                email = record.email or ""
                name = email
                res.append((record.id, name))
            return res
        if self._context.get("only_id_no"):
            res = []
            for record in self:
                ref = record.ref or ""
                name = ref
                res.append((record.id, name))
            return res
        return super(ResPartner, self).name_get()
