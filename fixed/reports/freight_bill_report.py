# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ReportFreightWithBills(models.AbstractModel):
    _name = 'report.fixed.report_freight_with_bills'
    _description = 'Freight report with bills lines'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': docids,
            'doc_model': 'fixed.freight_bill',
            'docs': self.env['fixed.freight_bill'].browse(docids),
            'report_type': data.get('report_type') if data else '',
        }
