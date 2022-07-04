# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    standard_bom = fields.Boolean('Having Standard BOM', default=False)
    non_standard_bom = fields.Boolean('Not having Standard BOM', default=False)
    alternative_code = fields.Char('Alternative Code')
    kfmi_code = fields.Char(string='KFMI Code')
    abb_code = fields.Char(string='KBB Code')
    sec_code = fields.Char(string='SEC Code')
    hide_sales = fields.Boolean(string='Hide Sale Price', compute='set_hide_sales')
    hide_cost = fields.Boolean(string='Hide Sale Cost', compute='set_hide_cost')
    arabic_name = fields.Char(string='Arabic Product Name')

    def set_hide_sales(self):
        if self.env.user.has_group('khalifa_customizations.group_hide_sale_price'):
            self.hide_sales = True
        else:
            self.hide_sales = False

    def set_hide_cost(self):
        if self.env.user.has_group('khalifa_customizations.group_hide_cost'):
            self.hide_cost = True
        else:
            self.hide_cost = False

    @api.onchange('standard_bom')
    def _onchange_standard_bom(self):
        if self.standard_bom:
            self.non_standard_bom = False

    @api.onchange('non_standard_bom')
    def _onchange_non_standard_bom(self):
        if self.non_standard_bom:
            self.standard_bom = False
    
    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.user.company_id and self.env.user.company_id.default_supplier_id:
            seller_ids = [(0,0,{'name':self.env.user.company_id.default_supplier_id.id})]
            res.update({
                'seller_ids':seller_ids
            })
        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if self._context.get('search_alternative_code'):
            args.insert(0, ('alternative_code','ilike',name))
            args.insert(0, ('name','ilike',name))
            args.insert(0, '|')
            product_ids = self.env['product.product'].search(args)
            return product_ids.ids
        res = super()._name_search(name, args, operator, limit, name_get_uid)
        return res

    def name_get(self):
        def _name_get(d):
            name = d.get('name', '')
            code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
            alt_code = d.get('alternate_code','')
            if code and alt_code:
                name = '[%s] %s [%s]' % (code,name,alt_code)
            elif code:
                name = '[%s] %s' % (code,name)
            elif alt_code:
                name = '%s [%s]' % (name,alt_code)
            return (d['id'], name)
        result = []
        for product in self.sudo():
            mydict = {
                        'id': product.id,
                        'name': product.name,
                        'default_code': product.default_code,
                        'alternate_code': product.alternative_code or '',
                        }
            result.append(_name_get(mydict))
        return result

    def get_product_multiline_description_sale(self):
        """
        Override method to change description in sale order line
        """
        print ('self.display_name', self.name)
        name = self.name
        if self.description_sale:
            name += '\n' + self.description_sale
        return name

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
