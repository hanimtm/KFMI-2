# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError


# class MrpProduction(models.Model):
#     _inherit = 'mrp.production'
#
#     branch_id = fields.Many2one('company.branch', string="Branch",
#         default=lambda self: self.env.user.branch_id)


# class MrpUnbuild(models.Model):
#     _inherit = 'mrp.unbuild'
#
#     branch_id = fields.Many2one('company.branch', string="Branch",
#         default=lambda self: self.env.user.branch_id)


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    branch_id = fields.Many2one('company.branch', string="Branch",
        default=lambda self: self.env.user.branch_id)


# class MrpBom(models.Model):
#     _inherit = 'mrp.bom'
#
#     branch_id = fields.Many2one('company.branch', string="Branch",
#         default=lambda self: self.env.user.branch_id)

# class MrpWorkOrder(models.Model):
#     _inherit = 'mrp.workorder'
#
#     branch_id = fields.Many2one('company.branch', string="Branch",
#         default=lambda self: self.env.user.branch_id)


# class MrpWorkCenter(models.Model):
#     _inherit = 'mrp.workcenter'
#
#     branch_id = fields.Many2one('company.branch', string="Branch",
#         default=lambda self: self.env.user.branch_id)


# class MrpRoutingWorkcenter(models.Model):
#     _inherit = 'mrp.routing.workcenter'
#
#     branch_id = fields.Many2one('company.branch', string="Branch",
#         default=lambda self: self.env.user.branch_id)