# -*- coding:utf-8 -*-

from odoo import fields, models, api
import xlwt
from xlwt import easyxf
import math
import io

selection_data = [
    ('normal', 'Manufacture this product', 'bom_type'), ('phantom', 'Kit', 'bom_type'),
    ('flexible', 'Allowed', 'consumption'), ('warning', 'Allowed with warning', 'consumption'),
    ('strict', 'Blocked', 'consumption'),
    ('draft', 'Draft', 'bom_state'), ('confirm', 'Confirm', 'bom_state'), ('revise', 'Revise', 'bom_state'),
    ('approve', 'Approved', 'bom_state'), ('cancel', 'Cancel', 'bom_state')
]


def _get_selections(category):
    data = filter(lambda x: x[2] == category, selection_data)
    return list(map(lambda x: (x[0], x[1]), data))


class BOMDummy(models.Model):
    _name = 'bom.dummy'
    _description = 'BOM Dummy'
    _rec_name = 'code'

    product_tmpl_id = fields.Many2one('product.template', string='Product', required=True)
    product_id = fields.Many2one('product.product', string='Product Variant')
    non_standard_bom = fields.Boolean(related='product_tmpl_id.non_standard_bom', string='Not having Standard BOM')
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    quantity = fields.Float(string='Quantity')
    code = fields.Char(string='Reference')
    label = fields.Char(string='Label')
    drawing = fields.Char(string='Drawing')
    bom_type = fields.Selection(lambda self: _get_selections('bom_type'), string='BoM Type', default='normal')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    consumption = fields.Selection(lambda self: _get_selections('consumption'), string='Flexible Consumption',
                                   default='warning')
    picking_type_id = fields.Many2one('stock.picking.type', string='Operation')
    bom_dummy_line_ids = fields.One2many('bom.dummy.line', 'bom_dummy_id', string='Components')
    state = fields.Selection(lambda self: _get_selections('bom_state'), string='BoM State', default='draft')
    bom_request_line_id = fields.Many2one('bom.request.line', string="Bom Request Line")
    order_line_id = fields.Many2one('sale.order.line', string='Order Line')
    request_id = fields.Many2one('bom.request', string='BOM Request')
    user_id = fields.Many2one('res.users', string='Assigned To')
    routing_id = fields.Many2one('mrp.routing', string='Routing')
    sec_wh_id = fields.Many2one('sec.wh', string='SEC WH')
    line_no = fields.Char(string="Line No")

    def confirm_bom(self):
        self.state = 'confirm'
        if self.bom_request_line_id:
            conirm = False
            bom_dummy_sates = [each.state for each in self.bom_request_line_id.request_id.bom_request_line_ids]
            result = all(each in ['confirm', 'approve'] for each in bom_dummy_sates)
            if result:
                self.bom_request_line_id.request_id.sudo().write({
                    'state': 'assigned',
                })

    def approve_bom(self):
        self.state = 'approve'
        # once all the bom request lines are approved update bom request state to confirmed.
        self.bom_request_line_id.request_id.update_state()
        mrp_bom_id = self.create_mrp_bom()
        if mrp_bom_id:
            self.order_line_id.write({
                'bom_id': mrp_bom_id.id,
                'drawing': mrp_bom_id.drawing,
                'label': mrp_bom_id.label,
            })
        # self.bom_request_line_id.request_id.need_dm_approval()

    def create_mrp_bom(self):
        vals = []
        for component in self.bom_dummy_line_ids:
            vals.append((0, 0, {
                'product_id': component.product_id.id,
                'product_qty': component.quantity,
                'product_uom_id': component.product_uom_id.id
            }))
        values = {
            'product_id': self.product_id.id,
            'product_tmpl_id': self.product_tmpl_id.id,
            'product_qty': self.quantity,
            'consumption': self.consumption,
            'type': self.bom_type,
            'bom_line_ids': vals,
            'code': self.code,
            'label': self.label,
            'drawing': self.drawing,
            'sec_wh_id': self.sec_wh_id and self.sec_wh_id.id or False,
            'line_no': self.line_no,
            'bom_dummy_id': self.id,
            'routing_id': self.routing_id.id,
        }
        bom_id = self.env['mrp.bom'].create(values)
        bom_id.onchange_routing()
        return bom_id

    def revise_bom(self):
        self.state = 'revise'
        if self.bom_request_line_id:
            self.bom_request_line_id.request_id.write({
                'state': 'revise',
            })

    def action_download_components(self):
        import base64
        filename = 'BOM_Components.xls'
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('BOM Components')
        num_style = easyxf(num_format_str='#,##0')
        first_col = worksheet.col(0)
        first_col.width = 256 * 30
        second_col = worksheet.col(1)
        second_col.width = 256 * 20
        three_col = worksheet.col(2)
        three_col.width = 256 * 20
        four_col = worksheet.col(5)
        four_col.width = 256 * 30
        five_col = worksheet.col(7)
        five_col.width = 256 * 20
        small_heading_style = easyxf(
            'font:  name  Century Gothic, bold on, color white , height 230 ; pattern: pattern solid,fore-colour dark_green; align: vert centre, horz center ;')
        medium_heading_style = easyxf(
            'font:name Arial, bold on,height 250, color  dark_green; align: vert centre, horz center ;')
        bold = easyxf('font: bold on ')
        worksheet.write_merge(0, 3, 0, 3, 'BOM COMPONENTS', medium_heading_style)
        worksheet.write_merge(5, 5, 0, 3, 'POS Products Details', medium_heading_style)
        worksheet.write(6, 0, 'Component Name', small_heading_style)
        worksheet.write(6, 1, 'Internal Reference', small_heading_style)
        worksheet.write(6, 2, 'Quantity', small_heading_style)
        worksheet.write(6, 3, 'UOM', small_heading_style)

        r = 7
        for line in self.bom_dummy_line_ids:
            worksheet.write(r, 0, line.product_id.name)
            worksheet.write(r, 1, str(line.product_id.default_code))
            worksheet.write(r, 2, str(line.quantity), num_style)
            worksheet.write(r, 3, line.product_uom_id.name)
            r = r + 1

        fp = io.BytesIO()
        workbook.save(fp)
        export_id = self.env['bom.excel.report'].create(
            {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()
        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'bom.excel.report',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        return True


class BoMDummyLine(models.Model):
    _name = 'bom.dummy.line'
    _description = 'BOM Dummy line'

    bom_dummy_id = fields.Many2one('bom.dummy', string='Dummy BOM')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    qty_available = fields.Float(related='product_id.qty_available', string='On Hand', readonly=True)
    qty_reserve = fields.Float(related='product_id.outgoing_qty', string='Reserved')
    purchase_price = fields.Float(string='Purchase Price', compute='get_purchase_price')
    product_value = fields.Float(string='Stock Value', compute='get_stock_value')
    product_uom_id = fields.Many2one('uom.uom', string='Product Unit of Measure')

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

    @api.depends('product_id')
    def get_purchase_price(self):
        for line in self:
            price = 0.0
            if line.product_id and line.product_id.id and isinstance(line.product_id.id, int):
                price = line.product_id.standard_price or 0.0
            line.purchase_price = price or 0.0

    @api.depends('product_id')
    def get_stock_value(self):
        for line in self:
            value = 0.0
            if line.product_id and line.product_id.id and isinstance(line.product_id.id, int):
                self._cr.execute(
                    'select sum(value) as value from stock_valuation_layer where product_id=%s;' % (line.product_id.id))
                result = self._cr.dictfetchall()
                value = result and result[0] and result[0].get('value')
            line.product_value = value or 0.0


class BomExcelReport(models.TransientModel):
    _name = "bom.excel.report"

    excel_file = fields.Binary('BOM Components Excel Report', readonly=True)
    file_name = fields.Char('Excel File', size=64, readonly=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
