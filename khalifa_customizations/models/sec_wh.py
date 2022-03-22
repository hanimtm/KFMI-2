# -*- coding:utf-8 -*-
from odoo import fields, models, api


class SecWh(models.Model):
    _name = 'sec.wh'
    _description = "SEC WH"

    name = fields.Char(string='Wherehouse Name', copy=False)
