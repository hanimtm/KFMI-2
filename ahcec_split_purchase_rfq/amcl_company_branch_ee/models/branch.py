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
from odoo.exceptions import ValidationError


class CompanyBranch(models.Model):
    _name = 'company.branch'
    _description = "Company's Branch"

    name = fields.Char(string="Branch Name", required=True)
    company_id = fields.Many2one('res.company', string="Company", required=True)
    phone = fields.Char(string="Phone")
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    parent_id = fields.Many2one('company.branch', string="Parent Branch")

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('Error ! You cannot create recursive Branch.'))


class ResUsers(models.Model):
    _inherit = 'res.users'

    def write(self, vals):
        self = self.sudo()
        res = super(ResUsers, self).write(vals)
        if vals.get('company_id') and not vals.get('branch_id'):
            branch_ids = self.env['company.branch'].search([('company_id', '=', vals.get('company_id'))])
            if branch_ids:
                for user in self:
                    user.sudo().branch_ids = False
                    user.sudo().branch_id = branch_ids[0].id
                    user.sudo().write({'branch_ids': [(6, 0, branch_ids.ids)]})
            else:
                raise ValidationError(_('There is no branch for company %s.' %
                                        (self.env['res.company'].browse(vals.get('company_id')).name)))
        self.env['ir.default'].clear_caches()
        return res

    @api.constrains('branch_id', 'branch_ids')
    def _check_company_branch(self):
        if any(user.branch_ids and user.branch_id not in user.branch_ids for user in self):
            raise ValidationError(_('The chosen branch is not in the allowed branches for this user'))

    @api.onchange('company_ids')
    def onchange_allow_companies(self):
        self.branch_ids = False
        if self.company_ids:
            branch_ids = self.env['company.branch'].search([('company_id', 'in', self.company_ids.ids)])
            self.branch_ids = branch_ids.ids

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id and not self.company_ids:
            branch_ids = self.env['company.branch'].search([('company_id', '=', self.company_id.id)])
            self.branch_id = branch_ids[0].id
            self.branch_ids = branch_ids.ids

    @api.model
    def _company_branch_unit(self):
        return self.env.user.branch_id

    @api.model
    def _company_branch_units(self):
        return self._company_branch_unit()

    branch_id = fields.Many2one('company.branch', string="Current Branch",
                                default=lambda self: self._company_branch_unit())
    branch_ids = fields.Many2many('company.branch', 'table_company_branch_users_rel', 'user_id', 'branch_id',
                                  string="Allowed Branches", default=lambda self: self._company_branch_units())

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
