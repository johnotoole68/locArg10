 # -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import UserError,ValidationError
from odoo.tools.safe_eval import safe_eval

from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _compute_vat_ledger_ref(self):
        for inv in self:
            if inv.type in ['in_invoice','in_refund']:
                for line in inv.invoice_line_ids:
                    if line.account_id:
                        inv.vat_ledger_ref = line.account_id.name


    @api.multi
    def _compute_cae_barcode(self):
        #company.partner_id.document_number,
        #o.journal_id.journal_class_id.afip_code,
        #o.journal_id.point_of_sale,
        #int(o.afip_cae or 0),
        #int(o.afip_cae_due is not False and flatdate(o.afip_cae_due) or 0)
        for inv in self:
            inv.cae_barcode = str(inv.company_id.partner_id.main_id_number) + str(inv.journal_id.journal_class_id.afip_code) + \
                            str(inv.journal_id.point_of_sale) + str(inv.afip_cae or 0) + str(inv.afip_cae_due or 0).replace('-','')

    cae_barcode = fields.Char('CAE Barcode',compute=_compute_cae_barcode)
    vat_ledger_ref = fields.Char('VAT Ledger Ref',compute=_compute_vat_ledger_ref)

class VatLedgerXlsx(ReportXlsx):

	def generate_xlsx_report(self, workbook, data, ledgers):
       		for obj in ledgers:
			if obj.type == 'sale':
		        	report_name = obj.name
        			# One sheet by partner
	        		sheet = workbook.add_worksheet(report_name[:31])
	        		bold = workbook.add_format({'bold': True})
		        	sheet.write(0, 0, obj.name, bold)
				headers = ['Fecha','Cpbte','Nro','Cliente','C.U.I.T.','IVA','Exento','Gravado','I.V.A.','S/S I.V.A.','I.Interno','S/S I.Int.','Percepcion','Total']
				index = 0
				for header in headers:
					sheet.write(3,index,header,bold)
					index = index + 1
				row_index = 4
				for inv in obj.invoice_ids:
					sheet.write(row_index,0,inv.date_invoice)
					sheet.write(row_index,1,inv.display_name[:5])
					sheet.write(row_index,2,inv.document_number)
					sheet.write(row_index,3,inv.partner_id.name)
					sheet.write(row_index,4,inv.partner_id.main_id_number)
					sheet.write(row_index,5,inv.partner_id.afip_responsability_type_id.name)
					sheet.write(row_index,6,inv.vat_exempt_base_amount)
					sheet.write(row_index,7,inv.vat_base_amount)
					sheet.write(row_index,8,inv.vat_amount)
					sheet.write(row_index,9,0)
					sheet.write(row_index,10,0)
					sheet.write(row_index,11,0)
					sheet.write(row_index,12,0)
					sheet.write(row_index,13,inv.amount_total)
					row_index = row_index + 1
			else:
		        	report_name = obj.name
        			# One sheet by partner
	        		sheet = workbook.add_worksheet(report_name[:31])
	        		bold = workbook.add_format({'bold': True})
		        	sheet.write(0, 0, obj.name, bold)
				headers = ['Fecha','Cpbte','Nro','Proveedor','C.U.I.T.','IVA','Gravado','No Gravado','I.V.A.','S/S I.V.A.','I.Interno','S/S I.Int.','P.IVA','P.IIBB','P.Gcias.','Total']
				index = 0
				for header in headers:
					sheet.write(3,index,header,bold)
					index = index + 1
				row_index = 4
				for inv in obj.invoice_ids:
					sheet.write(row_index,0,inv.date_invoice)
					sheet.write(row_index,1,inv.vat_ledger_ref)
					sheet.write(row_index,2,inv.display_name)
					sheet.write(row_index,3,inv.partner_id.name)
					sheet.write(row_index,4,inv.partner_id.main_id_number)
					sheet.write(row_index,5,inv.partner_id.afip_responsability_type_id.name)
					sheet.write(row_index,6,inv.vat_base_amount)
					sheet.write(row_index,7,inv.vat_exempt_base_amount)
					sheet.write(row_index,8,inv.vat_amount)
					sheet.write(row_index,9,0)
					sheet.write(row_index,10,0)
					sheet.write(row_index,11,0)
					sheet.write(row_index,12,0)
					sheet.write(row_index,13,0)
					sheet.write(row_index,14,0)
					sheet.write(row_index,15,inv.amount_total)
					row_index = row_index + 1



VatLedgerXlsx('report.account.vat.ledger.xlsx','account.vat.ledger')
