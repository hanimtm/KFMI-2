# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class DirectMaterial(models.Model):
    _name = "direct.material.transfer"
    _description = "Direct Material Transfer"
    _inherit = ['mail.thread']

    name = fields.Char(
        string="Name",
        required=True,
        copy=False,
        default='New',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env.user.company_id,
        states={'done': [('readonly', True)]},
        required=True
    )
    source_location_id = fields.Many2one(
        'stock.location',
        string="From",
        required=True,
        states={'done': [('readonly', True)]}
    )
    to_location = fields.Many2one(
        'stock.expense.location',
        string="To",
        required=True,
        states={'done': [('readonly', True)]}
    )
    destination_location_id = fields.Many2one(
        related='to_location.location',
        string="Destination Location",
        store=True
    )
    source_partner_id = fields.Many2one(
        'res.partner',
        string="Source Partner",
        # required=True,
        states={'done': [('readonly', True)]}
    )
    destination_partner_id = fields.Many2one(
        'res.partner',
        string="Destination Partner",
        # required=True,
        states={'done': [('readonly', True)]}
    )
    user_id = fields.Many2one(
        'res.users',
        string="Responsible Person",
        states={'done': [('readonly', True)]}
    )
    reason = fields.Text(
        string="Reason For Transfer",
        states={'done': [('readonly', True)]}
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic Account",
        states={'done': [('readonly', True)]}
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('done', 'Transferred'),
            ('cancelled', 'Cancelled'),
        ],
        string="Status",
        default='draft',
        tracking=True,
    )
    create_date = fields.Datetime(
        string="Create Date",
        default=fields.Datetime.now,
        readonly=True,
    )
    transferred_date = fields.Date(
        string="Transferred Date",
        states={'done': [('readonly', True)]}
    )
    received_user_id = fields.Many2one(
        'res.users',
        'Received By',
        readonly=True,
    )
    line_ids = fields.One2many('direct.material.line',
                               'direct_id',
                               string='Transfer Lines',
                               states={'done': [('readonly', True)]}
                               )
    expense_account = fields.Many2one(
        related='to_location.expense_account',
        string="Expense Account",
        store=True
    )
    stock_journal = fields.Many2one(
        'account.journal',
        string='Stock Journal',
        domain="[('type','=','general')]",
        required=True
    )
    account_move = fields.Many2one(
        'account.move',
        string='Account Entry',
        copy=False
    )

    @api.onchange('to_location')
    def _onchange_to_location(self):
        if self.to_location:
            if not self.to_location.expense_account or not self.to_location.location:
                raise ValidationError("Please add the Expense account or Location to To location")

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('direct.material')
        vals['name'] = name
        return super(DirectMaterial, self).create(vals)

    def unlink(self):
        for transfer in self:
            if transfer.state not in ['draft', 'cancelled']:
                raise ValidationError("Only delete in draft or cancelled state")
        return super(DirectMaterial, self).unlink()

    def act_submitted(self):
        for rec in self:
            rec.state = 'submitted'

    def act_approve(self):
        for rec in self:
            rec.state = 'approve'

    def _prepare_move_line_vals(self, move, line, quantity,new_move):
        self.ensure_one()
        vals = {
            'move_id': new_move.id,
            'product_id': line.product_id.id,
            'product_uom_id': line.product_uom.id,
            'location_id': move.source_location_id.id,
            'location_dest_id': move.destination_location_id.id,
            'picking_id': False,
            'company_id': move.company_id.id,
        }
        if quantity:
            rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            uom_quantity = line.product_id.uom_id._compute_quantity(quantity, line.product_uom,
                                                                    rounding_method='HALF-UP')
            uom_quantity = float_round(uom_quantity, precision_digits=rounding)
            uom_quantity_back_to_product_uom = line.product_uom._compute_quantity(uom_quantity, line.product_id.uom_id,
                                                                                  rounding_method='HALF-UP')
            if float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
                vals = dict(vals, qty_done=quantity)
            else:
                vals = dict(vals, qty_done=quantity, product_uom_id=line.product_id.uom_id.id)
        return vals

    def validate_lines(self):
        for line in self.line_ids:
            if line.product_onhand_qty <= 0:
                raise ValidationError("On Hand quantity must be more than zero(0).")

    def act_done(self):
        for rec in self:
            rec.validate_lines()
            for line in rec.line_ids:
                new_move = self.env['stock.move'].create({
                    'name': _('New Move:') + line.product_id.display_name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_qty,
                    'product_uom': line.product_uom.id,
                    'description_picking': 'Direct Transfer',
                    'location_id': rec.source_location_id.id,
                    'location_dest_id': rec.destination_location_id.id,
                    'company_id': rec.company_id.id,
                    'state': 'done'
                })

                new_move._action_confirm()
                new_move._action_assign()
                new_move._action_done()
                self.env['stock.move.line'].create(
                    self._prepare_move_line_vals(rec, line, line.product_qty,new_move))
                line.move_id = new_move.id
                # new_move.write({'state': 'done'})
            rec.transferred_date = fields.Date.today()
            rec.state = 'done'
        self.create_accounting_expense_entry()

    def act_cancel_manager(self):
        self.account_move.button_cancel()
        self.state = 'cancelled'

    def act_reset_draft(self):
        self.state = 'draft'

    def create_accounting_expense_entry(self):
        subline = []
        for line in self.line_ids:
            if not line.product_id.product_tmpl_id.categ_id.property_stock_account_output_categ_id:
                raise ValidationError("Please assign the Stock Output account in the Product Category")
            stock_output = (0, 0, {
                'account_id': line.product_id.product_tmpl_id.categ_id.property_stock_account_output_categ_id.id,
                'currency_id': self.company_id.currency_id.id,
                'debit': 0.0,
                'credit': line.product_qty * line.price_unit,
                'amount_currency': line.product_qty * line.price_unit,
            })
            subline.append(stock_output)
            if not self.expense_account:
                raise ValidationError("Please assign the Expense account in the Destination Location")
            expense_account = (0, 0, {
                'account_id': self.expense_account.id,
                'currency_id': self.company_id.currency_id.id,
                'debit': line.product_qty * line.price_unit,
                'analytic_account_id': self.analytic_account_id.id,
                'credit': 0.0,
                'amount_currency': line.product_qty * line.price_unit,
            })
            subline.append(expense_account)
            if not line.product_id.product_tmpl_id.categ_id.property_stock_valuation_account_id:
                raise ValidationError("Please assign the Stock valuation account in the product category    ")
            valuation_account = (0, 0, {
                'account_id': line.product_id.product_tmpl_id.categ_id.property_stock_valuation_account_id.id,
                'currency_id': self.company_id.currency_id.id,
                'debit': 0.0,
                'credit': line.product_qty * line.price_unit,
                'amount_currency': line.product_qty * line.price_unit,
            })
            subline.append(valuation_account)
            stock_account2 = (0, 0, {
                'account_id': line.product_id.product_tmpl_id.categ_id.property_stock_account_output_categ_id.id,
                'currency_id': self.company_id.currency_id.id,
                'debit': line.product_qty * line.price_unit,
                'credit': 0.0,
                'amount_currency': line.product_qty * line.price_unit,
            })
            subline.append(stock_account2)
        if subline:
            account_move = self.env['account.move'].create({
                'move_type': 'entry',
                'date': self.transferred_date,
                'line_ids': subline,
            })
            self.update({'account_move': account_move.id})


class DirectMaterialLine(models.Model):
    _name = 'direct.material.line'
    _description = 'Direct Material Line'

    name = fields.Char('Description',
                       index=True,
                       required=True
                       )
    sequence = fields.Integer('Sequence',
                              default=10
                              )
    create_date = fields.Datetime('Creation Date',
                                  index=True,
                                  readonly=True
                                  )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        default=lambda self: self.env.company,
        index=True,
        required=True
    )
    product_id = fields.Many2one(
        'product.product',
        'Product',
        check_company=True,
        domain="[('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        index=True,
        required=True,
        states={'done': [('readonly', True)]}
    )
    product_qty = fields.Float(
        'Real Quantity',
        digits=0,
        compute_sudo=True
    )
    product_uom = fields.Many2one('uom.uom',
                                  'Unit of Measure',
                                  required=True,
                                  )
    product_tmpl_id = fields.Many2one(
        'product.template',
        'Product Template',
        related='product_id.product_tmpl_id',
        readonly=False,
    )
    source_location_id = fields.Many2one(
        'stock.location',
        'Source Location',
        auto_join=True,
        index=True,
        required=True,
        check_company=True
    )
    destination_location_id = fields.Many2one(
        'stock.location',
        'Destination Location',
        auto_join=True,
        index=True,
        required=True,
        check_company=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Destination Address ',
        states={'done': [('readonly', True)]}
    )
    direct_id = fields.Many2one('direct.material.transfer',
                                'Direct Material',
                                index=True,
                                states={'done': [('readonly', True)]},
                                check_company=True
                                )
    state = fields.Selection(related='direct_id.state',
                             string='State',
                             store=True
                             )
    price_unit = fields.Float(
        'Unit Price',
        copy=False
    )
    origin = fields.Char("Source Document")
    move_id = fields.Many2one(
        'stock.move',
        'Stock Move'
    )
    product_onhand_qty = fields.Float(related="product_id.qty_available", string="On Hand")

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.product_uom = self.product_id.uom_id.id
            self.price_unit = self.product_id.standard_price
            self.product_tmpl_id = self.product_id.product_tmpl_id.id
