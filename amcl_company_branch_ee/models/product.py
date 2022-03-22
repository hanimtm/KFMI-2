from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    branch_id = fields.Many2many('company.branch', string="Branch", required=True)
