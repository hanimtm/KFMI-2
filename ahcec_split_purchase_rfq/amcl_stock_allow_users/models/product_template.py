from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    allowed_user_ids = fields.Many2many('res.users')#, compute='_compute_allowed_users', store=True
