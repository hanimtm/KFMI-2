# -*- coding: utf-8 -*-


import binascii

from num2words import num2words
from odoo import api, models, fields
from datetime import datetime
import pytz
import base64


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    tax_amount = fields.Monetary('Tax amount', compute='_compute_tax_amount', store=True)
    vat_text = fields.Char('Vat Text', compute='_get_vat_text', store=True)
    discount_amount = fields.Float('Discount Amount', compute='_compute_all_price', store=True)
    price_before_discount = fields.Monetary('Price B/f Disc', compute='_compute_all_price', store=True)

    @api.depends('tax_ids', 'price_unit', 'quantity')
    def _get_vat_text(self):
        vat = ''
        for line in self:
            for tax in line.tax_ids:
                vat += str(tax.amount) + '%,'
            line.vat_text = vat[:-1]

    @api.depends('discount', 'price_unit', 'quantity')
    def _compute_all_price(self):
        for line in self:
            line.price_before_discount = line.quantity * line.price_unit
            line.discount_amount = (line.price_before_discount * line.discount) / 100.0

    @api.depends('price_unit', 'quantity', 'price_subtotal', 'price_total')
    def _compute_tax_amount(self):
        for line in self:
            line.tax_amount = line.price_total - line.price_subtotal


class AccountMove(models.Model):
    _inherit = 'account.move'

    TAG_SELLER = 1
    TAG_VAT_NO = 2
    TAG_TIME_STAMP = 3
    TAG_TOTAL = 4
    TAG_VAT_TOTAL = 5

    amount_text = fields.Char(string='Amount In Words', compute='amount_to_words')
    amount_in_ar = fields.Char(string='Amount In Words', compute='amount_to_words')
    attention = fields.Many2one('res.partner', 'Attention', default=lambda self: self.partner_id.id)
    approved_by = fields.Many2one('res.partner', 'Approved By', default=lambda self: self.env.user.id)
    vat_text = fields.Char('Vat Text', compute='_get_vat_text')
    vat_arabic_text = fields.Char('Vat Text(Arabic)', compute='_get_vat_text')
    discount = fields.Float('Discount', compute='_compute_all_price')
    price_before_discount = fields.Monetary('Total ( Excluded VAT)', compute='_compute_all_price')
    delivery_date = fields.Date('Delivery Date')
    invoice_date_time = fields.Datetime('Invoice Date Time')
    po_number = fields.Char('PO Number')
    po_date = fields.Date('PO Date')
    wbs = fields.Char('WBS')
    gdn = fields.Char('GDN')

    @api.depends('invoice_line_ids', 'amount_untaxed', 'amount_tax')
    def _compute_all_price(self):
        price_before_discount = discount = 0
        for line in self.invoice_line_ids:
            price_before_discount += line.price_before_discount
            discount += line.discount_amount

        self.price_before_discount = price_before_discount
        self.discount = discount

    @api.depends('invoice_line_ids', 'amount_total')
    def _get_vat_text(self):
        vat = ''
        arab = ''
        for invoice in self:
            for tax in invoice.mapped('invoice_line_ids.tax_ids'):
                vat += str(tax.amount) + '%,'
                arab += str(tax.amount_in_arabic) + '%,'
            invoice.update({
                'vat_text': vat[:-1],
                'vat_arabic_text': arab[:-1]
            })

    def amount_to_words(self):
        for invoice in self:
            amount_in_eng = num2words(invoice.amount_total, to='currency',
                                      lang='en')
            amount_in_eng = amount_in_eng.replace('euro', 'riyals')
            amount_in_eng = amount_in_eng.replace('cents', 'halala')
            invoice.update({
                'amount_text': amount_in_eng,
                'amount_in_ar': num2words(invoice.amount_total, to='currency',
                                          lang='ar')
            })

    def _data_hex(self, value, tag):
        hex_tag = self._convert_int_to_hex(tag)
        hex_len = self._convert_int_to_hex(len(value.encode("UTF-8")))
        hex_val = self._convert_str_to_hex(value)
        return "%s%s%s" % (hex_tag, hex_len, hex_val)

    def _seller_hex(self, value):
        return self._data_hex(value, self.TAG_SELLER)

    def _vat_no_hex(self, value):
        return self._data_hex(value, self.TAG_VAT_NO)

    def _time_stamp_hex(self, value):
        return self._data_hex(value, self.TAG_TIME_STAMP)

    def _total_hex(self, value):
        return self._data_hex(value, self.TAG_TOTAL)

    def _vat_total_hex(self, value):
        return self._data_hex(value, self.TAG_VAT_TOTAL)

    def _convert_int_to_hex(self, value):
        return "%0.2x" % value

    def _convert_str_to_hex(self, value):
        hex_val = ""
        if value:
            str_bytes = value.encode("UTF-8")
            encoded_hex = binascii.hexlify(str_bytes)
            hex_val = encoded_hex.decode("UTF-8")

        return hex_val

    def _convert_text_to_base64(self, value):
        # value_bytes = value.decode('utf-8')
        base64_bytes = base64.b64encode(value)
        return base64_bytes.decode("utf-8")

    def generate_tlv_code(self):
        self.invalidate_cache()
        DEFAULTE_TZ = 'Asia/Riyadh'
        hex_seller = False
        hex_vat_no = False
        hex_time_stamp = False
        total = False
        vat_total = False
        # time_stamp = datetime.now(
        #     pytz.timezone(self.env.user.tz or self._context.get('tz', DEFAULTE_TZ))).strftime('%Y-%m-%dT%H:%M:%SZ')

        localFormat = "%Y-%m-%d %H:%M:%S"

        # Convert date to current user timezone or Saudi Arabia in default case.
        if self.invoice_date_time:
            utcmoment_naive = datetime.strptime(str(self.invoice_date_time), localFormat)
        else:
            utcmoment_naive = self.create_date
        utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)

        tz_ = self.env.user.tz or self._context.get('tz', DEFAULTE_TZ)
        localDatetime = utcmoment.astimezone(pytz.timezone(tz_))

        time_stamp = localDatetime.strftime('%Y-%m-%dT%H:%M:%SZ')
        hex_seller = self._seller_hex(self.company_id.name or "")
        hex_vat_no = self._vat_no_hex(self.company_id.vat or "")
        hex_time_stamp = self._time_stamp_hex(time_stamp)
        hex_total = self._total_hex(str(self.amount_total))
        hex_vat_total = self._vat_total_hex(str(self.amount_tax))

        hex_text = "%s%s%s%s%s" % (hex_seller, hex_vat_no, hex_time_stamp, hex_total, hex_vat_total)
        code_qr = self._convert_text_to_base64(bytearray.fromhex(hex_text))

        return code_qr

    def invoice_validate(self):
        analytic = self.invoice_line_ids.mapped('account_analytic_id')
        if len(analytic) != 1:
            analytic = False
        if self.default_analytic:
            analytic = self.default_analytic
        if analytic is not False:
            for line in self.move_id.line_ids:
                if line.account_id.id == self.account_id.id:
                    line.write({'analytic_account_id': analytic.id, 'partner_id': self.partner_id.id})
        return super(AccountMove, self).invoice_validate()

    @api.onchange('partner_id')
    def onchange_partner_for_attention(self):
        if self.partner_id:
            self.attention = self.partner_id.id


class AccountTax(models.Model):
    _inherit = 'account.tax'

    amount_in_arabic = fields.Float('Amount in Arabic')
