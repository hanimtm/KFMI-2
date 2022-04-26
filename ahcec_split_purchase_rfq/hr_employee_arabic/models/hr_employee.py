# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    arabic_name = fields.Char(
        string="Name",
        required=True,
    )

    @api.model
    def create(self, vals):
        if vals.get('name'):
            partner = self.env['res.partner'].sudo().create({
                'name': vals.get('name'),
            })
            msg = _('New contact is created from employee module <br/> Created by : %s', (self.env.user.name))
            partner.message_post(body=msg)
            vals['address_home_id'] = partner.id
        employee = super(HrEmployee, self).create(vals)

        return employee
