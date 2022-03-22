# -*- coding: utf-8 -*-

from odoo import models, fields


class BOMRequestAssign(models.TransientModel):
    _name = 'bom.request.assign'
    _description = 'BOM Request Assign'

    bom_request_id = fields.Many2one('bom.request', string='Request Number', readonly=True, store=True)
    user_id = fields.Many2one('res.users', string='Assign To', required=True)
    assign_date = fields.Date(string='Assign Date', default=fields.Date.context_today)

    def assign_bom(self):
        if self.user_id:
            self.bom_request_id.write({
                'state': 'assigned',
                'user_id': self.user_id.id
            })
            template_id = self.env.ref('khalifa_customizations.notify_design_manager_mail_template')
            template_id.sudo().send_mail(self.id, force_send=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
