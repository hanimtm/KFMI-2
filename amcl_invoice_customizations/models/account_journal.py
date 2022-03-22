from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_a_petty_cash = fields.Boolean('Is a petty cash Journal')
