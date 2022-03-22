# -*- coding: utf-8 -*-
from odoo import fields, models
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
import io
import base64
import tempfile
import binascii
import xlrd
from odoo.exceptions import ValidationError


class GenerateComponents(models.TransientModel):
    _name = 'generate.components'
    _description = 'Generate Components Wizard'

    action = fields.Selection([('import', 'Import Components'), ('dwn_sample', 'Download Sample')], string='Action', default='import')
    data_file = fields.Binary(string='File')

    def generate_file(self):
        """
        generate demo file with headers.
        """
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Generate Data File')
        worksheet.write(0, 0, 'Name')
        worksheet.write(0, 1, 'Internal Reference')
        worksheet.write(0, 2, 'Quantity')
        worksheet.write(0, 3, 'Unit Of Measure')
        stream = io.BytesIO()
        workbook.save(stream)
        download_file_id = self.env['download.file'].create(
            {'file_name': 'Sample File.xls',
             'data_file': base64.encodestring(
                 stream.getvalue())})
        return {
            'name': 'Download file',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'download.file',
            'res_id': download_file_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
    
    def prepered_data_from_sheet(self, sheet):
        error_message = ''
        values = []
        for row_no in range(sheet.nrows):
            if row_no <= 0:
                fields = map(lambda row: row.value.encode('utf-8'),
                             sheet.row(row_no))
            else:
                record_data = {}
                internal_reference = sheet.cell_value(row_no, 1)
                product_id = self.env['product.product'].search([('default_code','=',internal_reference)], limit=1)
                if not product_id:
                    raise ValidationError('No product with internal reference "%s" exist on line %s.'%(internal_reference,row_no+1))
                quantity = sheet.cell_value(row_no, 2)
                record_data.update({
                    'product_id': product_id.id,
                    'quantity': quantity or 1
                })
                uom = sheet.cell_value(row_no, 3)
                uom_id = False
                if uom:
                    uom_id = self.env['uom.uom'].search([('name','ilike',uom)], limit=1)
                if not uom_id:
                    uom_id = product_id.uom_id
                record_data.update({
                    'product_uom_id': uom_id.id
                })
                values.append(record_data)
        return values
    
    def import_data_file(self):
        """
        import components
        """
        if not self.data_file:
            raise ValidationError('Please Add .xls file to import.')
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.data_file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        file_data = self.prepered_data_from_sheet(sheet)
        dummy_bom_id = self.env['bom.dummy'].browse(self._context.get('active_id'))
        values = []
        for each in file_data:
            values.append((0,0,each))
        dummy_bom_id.write({
            'bom_dummy_line_ids': values
        })


class DownloadFile(models.TransientModel):
    _name = 'download.file'
    _description = 'Download File'

    data_file = fields.Binary(string='Sample File')
    file_name = fields.Char(
        string='File Name',
        help='Save File as .xls format',
        default='Download File.xls')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
