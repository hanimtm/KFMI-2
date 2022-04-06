from odoo import api, fields, models, tools,_
from num2words import num2words


class PaymentRequest(models.Model):
    _name = 'payment.request'
    _inherit = 'mail.thread'

    @api.depends('company_id')
    def get_currency(self):
        company = self.env.company
        if company and company.currency_id:
            return company.currency_id.id
        return False

    name = fields.Char('Sequence', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    reference = fields.Char('Reference')
    lpo_num = fields.Many2one('purchase.order', string="LPO")
    company = fields.Many2one('res.partner', string="Company")
    payment_term = fields.Many2one('account.payment.term', string="Payment Term")
    amount = fields.Float('Amount')
    balance_amount = fields.Float('Balance', compute="compute_balance_amount")
    prepared = fields.Many2one('res.users', string="Prepared By")
    approved = fields.Many2one('res.users', string="Approved By")
    account_approve = fields.Many2one('res.users', string="Accounts Approved By")
    project = fields.Many2one('account.analytic.account', string="Projects")
    department_manager_comment = fields.Text(string="Department Manager Comment")
    account_comment = fields.Text(string="Accounts Comment")
    purchase_comment = fields.Text(string="Purchase Comment")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('manager_approval', 'Manager Approval'),
        ('accounts_approval', 'Accounts Approval'),
        ('manager_reject', 'Manager Rejected'),
        ('accounts_reject', 'Accounts Rejected'),
        ('approved', 'Approved'),
    ], string='Status', readonly=True, copy=False, index=True, track_sequence=3,
        default='draft')
    currency_id = fields.Many2one(
        'res.currency', string='Currency', default=get_currency, help="The payment's currency.")
    bank_id = fields.Many2one('res.bank', 'Bank Name')
    res_partner_bank_id = fields.Many2one('res.partner.bank', 'Account Number')
    bank_country_id = fields.Many2one('res.country', 'Bank Country')
    method_of_payment = fields.Char('Method Of Payment')
    reason_for_payment = fields.Text('Reason for The Payment')

    @api.depends('amount', 'lpo_num')
    def compute_balance_amount(self):
        """
        :return:
        """
        for rec in self:
            if rec.lpo_num:
                rec.balance_amount = rec.lpo_num.amount_total - rec.amount
            else:
                rec.balance_amount - 0.00

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('payment.request') or 'New'
        return super(PaymentRequest, self).create(vals)

    @api.onchange('lpo_num')
    def _get_data(self):
        for rec in self:
            rec.company = rec.lpo_num and rec.lpo_num.partner_id.id or False
            rec.payment_term = rec.lpo_num and rec.lpo_num.payment_term_id.id or False
            rec.amount = rec.lpo_num and rec.lpo_num.amount_total or 0
            #rec.project = rec.lpo_num.analytic_id.id


    def action_confirm(self):
        self.write({'state': 'manager_approval', 'prepared': self.env.user.id})
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


    def action_department_approve(self):
        self.write({'state': 'accounts_approval', 'approved': self.env.user.id})
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

    def action_department_reject(self):
        self.write({'state': 'manager_reject'})
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


    def action_accounts_approve(self):
        self.write({'state': 'approved', 'account_approve': self.env.user.id})
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


    def action_accounts_reject(self):
        self.write({'state': 'accounts_reject'})
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
        self.write({'state':'draft','account_approve':False,'approved':False})

    def get_num2words(self, number=0):
        """
        :return:
        """
        return num2words(number)
