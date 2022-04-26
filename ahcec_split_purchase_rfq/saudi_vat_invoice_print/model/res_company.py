# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class inherit_res_company(models.Model):
    _inherit= 'res.company'
    
    header_img = fields.Binary("Header Image")
    footer_img = fields.Binary("Footer Image")
    arabic = fields.Char('اسم')
    arabic_vat = fields.Char('ضريبة القيمة المضافة')
    street_arabic = fields.Char('شارع')
    street2_arabic = fields.Char('شارع 2')
    city_arabic = fields.Char('مدينة')
    state_arabic = fields.Char('حالة')
    zip_arabic = fields.Char('أزيز')
    country_arabic = fields.Char('بلد')



class ResBank(models.Model):
    _inherit= 'res.bank'

    iban = fields.Char('IBAN')
    branch = fields.Char('Branch')