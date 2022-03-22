# -*- coding:utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import ValidationError

selection_data = [
    ('draft', 'Draft', 'bom_request_status'), ('assigned', 'Assigned', 'bom_request_status'), ('revise', 'Revise', 'bom_request_status'), ('confirmed', 'Confirmed', 'bom_request_status'),('cancel', 'Cancel', 'bom_request_status'),
]

def _get_selections(category):
    data = filter(lambda x: x[2] == category, selection_data)
    return list(map(lambda x: (x[0], x[1]), data))


class BOMRequest(models.Model):
    _name = 'bom.request'
    _description = 'BOM Request'

    name = fields.Char(string='Request Number', readonly=True, store=True)
    user_id = fields.Many2one('res.users', string='Assign To')
    order_id = fields.Many2one('sale.order', string='Order')
    customer_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Customer')
    salesperson_id = fields.Many2one('res.users', related='order_id.user_id', string='Salesperson')
    bom_request_line_ids = fields.One2many('bom.request.line', 'request_id', string='BOM Request Line')
    state = fields.Selection(lambda self: _get_selections('bom_request_status'), string="Status", default='draft')
    read_for_user = fields.Boolean(string='Read For User', compute='set_read_for_user')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Request Number must be unique.'),
    ]

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            name = self.env['ir.sequence'].next_by_code('bom.request')
            vals.update({
                'name': name
            })
        res = super(BOMRequest, self).create(vals)
        return res
    
    def assign_bom_request(self):
        context = {
            'default_bom_request_id': self.id,
        }
        return {
            'name': 'Assign BOM',
            'type': 'ir.actions.act_window',
            'res_model': 'bom.request.assign',
            'view_mode': 'form',
            'target': 'new',
            'context': context
        }

    def cancel_dummy_bom(self):
        bom_dummy_ids = self.env['bom.dummy'].search([('bom_request_line_id','in',self.bom_request_line_ids.ids)])
        for each in bom_dummy_ids:
            each.state = 'cancel'
    
    @api.depends('user_id')
    def set_read_for_user(self):
        result = True
        if self.env.user.has_group('khalifa_customizations.design_manager'):
            result = False
        self.read_for_user = result

    def update_state(self):
        bom_dummy_ids = self.env['bom.dummy'].search([('bom_request_line_id','in',self.bom_request_line_ids.ids)])
        approve_flag = True
        # bom_dummy_state = [each.state for each in bom_dummy_ids]
        for each in bom_dummy_ids:
            if each.state not in ['approve']:
                approve_flag = False
        if approve_flag:
            self.write({
                'state': 'confirmed',
            })
    
    # def need_dm_approval(self):
    #     # changes state of quotation if there are any products in line that is non-standard and have BOM added.
    #     need_approval = []
    #     for line in self.order_id.order_line:
    #         if line.product_id.non_standard_bom and line.bom_id:
    #             need_approval.append(True)
    #     if all(need_approval):
    #         self.order_id.write({
    #             'state': 'sm_approve',
    #         })



class BOMRequestLine(models.Model):
    _name = 'bom.request.line'
    _description = 'BOM Request Line'

    request_id = fields.Many2one('bom.request', string='BOM Request')
    product_id = fields.Many2one('product.product', string='Product')
    description = fields.Char(string='Description')
    label = fields.Char(string='Label')
    drawing = fields.Char(string='Drawing')
    quantity = fields.Float(string='Quantity')
    product_uom_id = fields.Many2one('uom.uom', string='Unit Of Measure')
    order_line_id = fields.Many2one('sale.order.line', string='Order line')
    user_id = fields.Many2one(related='request_id.user_id', string='Assigned To')
    bom_dummy_id = fields.Many2one('bom.dummy', string='Dummy BOM')
    state = fields.Selection(related='bom_dummy_id.state', string='State')
    sec_wh_id = fields.Many2one('sec.wh', 'SEC WH')
    line_no = fields.Char(string="Line No")

    def create_or_view_bom_dummy(self):
        if self.request_id.state in ['assigned','revise','confirmed','cancel']:
            context = dict(self.env.context)
            # bom_dummy_id = self.env['bom.dummy'].sudo().search([('bom_request_line_id', '=', self.id)])
            action = {
                'name': 'BOM',
                'type': 'ir.actions.act_window',
                'res_model': 'bom.dummy',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
            }
            if not self.bom_dummy_id:
                sequence = self.env['ir.sequence'].next_by_code('bom.dummy')
                code = self.order_line_id.order_id.name + '-' + self.request_id.name + '-' + sequence
                values = {
                    'product_tmpl_id': self.product_id.product_tmpl_id.id,
                    'product_id': self.product_id.id,
                    'label': self.label,
                    'drawing': self.drawing,
                    'sec_wh_id': self.sec_wh_id and self.sec_wh_id.id or False,
                    'line_no': self.line_no,
                    'product_uom_id': self.product_uom_id.id,
                    'quantity': self.quantity,
                    'code': code,
                    'bom_request_line_id': self.id,
                    'order_line_id': self.order_line_id.id,
                    'request_id': self.request_id.id,
                    'user_id': self.user_id.id,
                }
                bom_dummy_id = self.env['bom.dummy'].sudo().create(values)
                # adding dummy_bom_id so latter it can be back tracked
                self.bom_dummy_id = bom_dummy_id.id
                action.update({
                    'res_id': bom_dummy_id.id
                })
                return action
            else:
                action.update({'res_id': self.bom_dummy_id.id})
                return action
        elif self.request_id.state == 'draft':
            raise ValidationError('BOM Request must be assigned.')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
