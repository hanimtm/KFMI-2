from odoo import api, fields, models, tools,_

class PaymentRequest(models.Model):
    _name = 'payment.request'
    _inherit = 'mail.thread'

    name = fields.Char('Sequence', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'),
                       track_visibility="onchange")
    lpo_num = fields.Many2one('purchase.order', string="LPO")
    company = fields.Many2one('res.partner', string="Company")
    payment_term = fields.Many2one('account.payment.term', string="Payment Term")
    amount = fields.Float('Amount')
    prepared = fields.Many2one('res.users', string="Prepared By")
    approved = fields.Many2one('res.users', string="Approved By")
    account_approve = fields.Many2one('res.users', string="Accounts Approved By")
    project = fields.Many2one('account.analytic.account', string="Projects")
    department_manager_comment = fields.Text(string="Department Manager Comment")
    account_comment = fields.Text(string="Accounts Comment")
    purchase_comment = fields.Text(string="Purchase Comment")
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Department Approval', 'Department Manager Approval'),
        ('Accounts Approval', 'Accounts Approval'),
        ('Department Reject', 'Department Manager Rejected'),
        ('Accounts Reject', 'Accounts Rejected'),
        ('Approved', 'Approved'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3,
        default='Draft')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('payment.request') or 'New'
        return super(PaymentRequest, self).create(vals)

    @api.onchange('lpo_num')
    def _get_data(self):
        for rec in self:
            rec.company = rec.lpo_num.partner_id.id
            rec.payment_term = rec.lpo_num.payment_term_id.id
            rec.amount = rec.lpo_num.amount_total
            #rec.project = rec.lpo_num.analytic_id.id

   # @api.multi
    def action_confirm(self):
        self.write({'state': 'Department Approval', 'prepared': self.env.user.id})
        channel_all_employees = self.env.ref('amcl_payment_request.channel_all_payment_request').read()[0]
        template_new_employee = self.env.ref('amcl_payment_request.email_template_data_payment_request').read()[0]
        # raise ValidationError(_(template_new_employee))
        if template_new_employee:
            # MailTemplate = self.env['mail.template']
            body_html = template_new_employee['body_html']
            subject = template_new_employee['subject']
            # raise ValidationError(_('%s %s ') % (body_html,subject))
            ids = channel_all_employees['id']
            channel_id = self.env['mail.channel'].search([('id', '=', ids)])
            body = """Hello, Payment Request with number %s Sending to purchase department approval""" % (self.name)
            channel_id.message_post(body=body, subject='Payment Request',subtype_ids='mail.mt_comment')

   # @api.multi
    def action_department_approve(self):
        self.write({'state': 'Accounts Approval', 'approved': self.env.user.id})
        channel_all_employees = self.env.ref('amcl_payment_request.channel_all_to_approve_payment_request').read()[0]
        template_new_employee = self.env.ref('amcl_payment_request.email_template_data_to_approve_payment_request').read()[0]
        # raise ValidationError(_(template_new_employee))
        if template_new_employee:
            # MailTemplate = self.env['mail.template']
            body_html = template_new_employee['body_html']
            subject = template_new_employee['subject']
            # raise ValidationError(_('%s %s ') % (body_html,subject))
            ids = channel_all_employees['id']
            channel_id = self.env['mail.channel'].search([('id', '=', ids)])
            body = """This payment request %s waiting for accounts approval""" % (self.name)
            channel_id.message_post(body=body, subject='Payment Request', subtype_ids='mail.mt_comment')

   # @api.multi
    def action_department_reject(self):
        self.write({'state': 'Department Reject'})
        channel_all_employees = self.env.ref('amcl_payment_request.channel_all_payment_request').read()[0]
        template_new_employee = self.env.ref('amcl_payment_request.email_template_data_payment_request').read()[0]
        # raise ValidationError(_(template_new_employee))
        if template_new_employee:
            # MailTemplate = self.env['mail.template']
            body_html = template_new_employee['body_html']
            subject = template_new_employee['subject']
            # raise ValidationError(_('%s %s ') % (body_html,subject))
            ids = channel_all_employees['id']
            channel_id = self.env['mail.channel'].search([('id', '=', ids)])
            body = """This payment request %s get rejected by the purchase department manager""" % (self.name)
            channel_id.message_post(body=body, subject='Payment Request', subtype_ids='mail.mt_comment')

   # @api.multi
    def action_accounts_approve(self):
        self.write({'state': 'Approved', 'account_approve': self.env.user.id})
        channel_all_employees = self.env.ref('amcl_payment_request.channel_all_payment_request').read()[0]
        template_new_employee = self.env.ref('amcl_payment_request.email_template_data_payment_request').read()[0]
        # raise ValidationError(_(template_new_employee))
        if template_new_employee:
            # MailTemplate = self.env['mail.template']
            body_html = template_new_employee['body_html']
            subject = template_new_employee['subject']
            # raise ValidationError(_('%s %s ') % (body_html,subject))
            ids = channel_all_employees['id']
            channel_id = self.env['mail.channel'].search([('id', '=', ids)])
            body = """This payment request %s is approved by the accounts team""" % (self.name)
            channel_id.message_post(body=body, subject='Payment Request', subtype_ids='mail.mt_comment')

   # @api.multi
    def action_accounts_reject(self):
        self.write({'state': 'Accounts Reject'})
        channel_all_employees = self.env.ref('amcl_payment_request.channel_all_payment_request').read()[0]
        template_new_employee = self.env.ref('amcl_payment_request.email_template_data_payment_request').read()[0]
        # raise ValidationError(_(template_new_employee))
        if template_new_employee:
            # MailTemplate = self.env['mail.template']
            body_html = template_new_employee['body_html']
            subject = template_new_employee['subject']
            # raise ValidationError(_('%s %s ') % (body_html,subject))
            ids = channel_all_employees['id']
            channel_id = self.env['mail.channel'].search([('id', '=', ids)])
            body = """This payment request %s is rejected by the accounts team""" % (self.name)
            channel_id.message_post(body=body, subject='Payment Request', subtype_ids='mail.mt_comment')

    #@api.multi
    def set_to_draft(self):
        self.write({'state':'Draft','account_approve':False,'approved':False})