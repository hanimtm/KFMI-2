# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class InheritResCompany(models.Model):
    _inherit = 'res.company'

    fax = fields.Char('Fax')
    arabic_phone = fields.Char('هاتف')
    arabic_fax = fields.Char('فاكس')
    arabic_cr = fields.Char('رقم سجل الشركة.')