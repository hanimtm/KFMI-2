from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError

from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter

class StockMove(models.Model):
    _inherit = 'stock.move'

    wip_quantity = fields.Float('WIP Quantity')
    wip_entry = fields.Many2one('account.move','WIP Entry')
    picking_origin = fields.Char(related='picking_id.origin',string='Picking Origin')


    def _is_internal(self):
        self.ensure_one()
        return self.location_id.usage == 'internal' \
            and self.location_dest_id.usage == 'internal'


class StockLocation(models.Model):
    _inherit = "stock.location"

    valuation_wip_account_id = fields.Many2one(
        'account.account', 'WIP Valuation Account',
        domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)],
        )

    force_accounting_entries = fields.Boolean(
        string='Force accounting entries?',
    )

    @api.constrains(
        'usage',
        'force_accounting_entries',
    )
    def _check_force_accounting_entries_internal_only(self):
        for loc in self:
            if loc.usage != 'internal' and loc.force_accounting_entries:
                raise ValidationError(_(
                    'You cannot force accounting entries'
                    ' on a non-internal locations.'))

    @api.constrains(
        'force_accounting_entries',
        'valuation_in_account_id',
        'valuation_out_account_id',
        'valuation_wip_account_id'
    )
    def _check_internal_valuation_accounts_present(self):
        """Ensure that every location requiring entries has valuation accs."""
        for loc in self:
            if loc.usage != 'internal' or not loc.force_accounting_entries:
                continue  # this one doesn't require accounts, it's fine
            if not loc.valuation_in_account_id \
                    or not loc.valuation_out_account_id:
                raise ValidationError(_(
                    'You must provide a valuation in/out accounts'
                    ' in order to force accounting entries.'))

    @api.onchange('usage')
    def _onchange_usage(self):
        for location in self:
            if location.usage != 'internal':
                location.update({'force_accounting_entries': False})


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _action_done (self):
        res = super(StockPicking, self)._action_done()
        for move in self.move_lines.filtered(lambda x: x.state == 'done'):
            self._account_wip_entry_move(move)


    def _create_wip_account_move_line(self,move, credit_account_id, debit_account_id, journal_id):
        self.ensure_one()
        AccountMove = self.env['account.move']
        quantity = move.product_qty

        # Make an informative `ref` on the created account move to differentiate between classic
        # movements, vacuum and edition of past moves.
        ref = self.name

        value = abs(self.env['stock.valuation.layer'].search([('stock_move_id','=',move.id)],limit=1).value)
        if value == 0:
            value = move.product_uom_qty * move.product_id.standard_price

        move_lines = self.with_context(forced_ref=ref)._prepare_wip_move_line(move,quantity, value, credit_account_id, debit_account_id)
        if move_lines:
            date = self._context.get('force_period_date', fields.Date.context_today(self))
            new_account_move = AccountMove.sudo().create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': ref,
                'stock_move_id': move.id,
            })
            new_account_move.post()
            move.write({'wip_entry':new_account_move.id})
            

    def _account_wip_entry_move(self,move):
        self.ensure_one()
        
        location_from = self.location_id
        location_to = self.location_dest_id
        company_from = self.company_id
        company_to = self.company_id

        accounts_data = self.product_id.product_tmpl_id.get_product_accounts()
        journal_id = accounts_data['stock_journal']
        if journal_id:
            if location_to and location_to.force_accounting_entries:  # goods returned from customer
                acc_dest = location_to.valuation_in_account_id.id
                acc_valuation = location_to.valuation_wip_account_id.id
                self.with_context(force_company=company_to.id)._create_wip_account_move_line(move,acc_dest, acc_valuation, journal_id.id)
            if location_from and location_from.force_accounting_entries:
                acc_dest = location_from.valuation_wip_account_id.id
                acc_valuation = location_from.valuation_in_account_id.id
                self.with_context(force_company=company_to.id)._create_wip_account_move_line(move,acc_dest, acc_valuation, journal_id.id)

    
    def _prepare_wip_move_line(self,move, qty, cost, credit_account_id, debit_account_id):
        self.ensure_one()

        valuation_amount = cost

        ref = self.name

        # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before creating the accounting entries.
        debit_value = self.company_id.currency_id.round(valuation_amount)

        # check that all data is correct
        credit_value = debit_value

        partner_id = (self.partner_id and self.env['res.partner']._find_accounting_partner(self.partner_id).id) or False
        debit_line_vals = {
            'name': self.name +'/ WIP /' + (self.origin or ''),
            'product_id': move.product_id.id,
            'quantity': qty,
            'product_uom_id': move.product_id.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'debit': debit_value if debit_value > 0 else 0,
            'credit': -debit_value if debit_value < 0 else 0,
            'account_id': debit_account_id,
        }
        credit_line_vals = {
            'name': self.name +'/ WIP /' + (self.origin or ''),
            'product_id': move.product_id.id,
            'quantity': qty,
            'product_uom_id': move.product_id.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': credit_account_id,
        }
        res = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        return res
