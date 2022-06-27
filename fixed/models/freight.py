# -*-coding: utf-8 -*-
# freight.py
#!/usr/bin/env python3
"""
    Create a model for a collection of errors

    Available field:
    - _name : A uniquely identified field for a class, Other classes can refer to this class through this field。
    - _description : Similar to tags, improves query friendliness
    - name : When other models refer to the record, it is used as a title

"""
from odoo import models, fields, api
import datetime
import pytz


class Freight(models.Model):
    _name = 'fixed.freight_bill'
    _description = 'freight_bill'
    # _rec_name = 'position_id'

    @api.one
    @api.depends('freight_line_ids.total_prices', 'date_invoice')
    def _compute_amount(self):
        self.amount_total = sum(line.total_prices for line in self.freight_line_ids)
        self.amount_total_signed = self.amount_total

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

    @api.model
    def get_location_time(self):
        now_time = datetime.datetime.utcnow()
        tz = self.env.user.tz or 'Asia/Shanghai'
        return str(now_time.replace(tzinfo=pytz.timezone(tz)))

    @api.model
    def _default_name(self):
        freight_time = '货单'
        return freight_time

    @api.multi
    def get_portal_url(self, report_type=None, download=False):
        if download and report_type:
            return '/freight/' + self.name + '?report_type=' + report_type + '&download=' + str(download)
        elif report_type:
            return '/freight/' + self.name + '?report_type=' + report_type
        else:
            return '/freight/' + self.name

    @api.multi
    def preview_freight(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

    name = fields.Char(string='name', default=_default_name)
    # position_id = fields.Char(string='发票编辑', states={'open': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string="客户名称", required=True, readonly=True,
                                  states={'open': [('readonly', False)]})
    salesclerk = fields.Many2one('res.users', string="销售员", readonly=True, states={'open': [('readonly', False)]})
    amount_total = fields.Monetary(string='总计', store=True, readonly=True, compute='_compute_amount',
                                   currency_field='currency_id',
                                   help="Total amount in the currency of the freight bill, negative for credit notes.")
    amount_total_signed = fields.Monetary(string='总计', store=True, readonly=True, compute='_compute_amount',
                                          currency_field='currency_id',
                                          help="Total amount in the currency of the invoice, negative for credit notes."
                                          )
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, readonly=True, states={'draft': [('readonly', False)]},
                                  default=_default_currency, track_visibility='always'
                                  )
    date_invoice = fields.Date(string='开票日期', readonly=True, index=True, states={'open': [('readonly', False)]},
                               help="Keep empty to use the current date", copy=False,
                               default=lambda self: self.env['fixed.freight_bill'].get_location_time()
                               )
    freight_line_ids = fields.One2many('fixed.freight_bill.line', 'freight_id',
                                       string='Invoice Lines',
                                       states={'open': [('readonly', False)]},
                                       readonly=True,
                                       copy=True)
    state = fields.Selection([
            ('open', 'Open'),
            ('cancel', 'Cancelled'),
        ], string='Status', index=True, readonly=True, default='open',
        track_visibility='onchange', copy=False,
        help=" * The 'Open' status is used when user creates invoice, an invoice number is generated. "
             "          It stays in the open status till the user pays the invoice.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")


class FreightBillLine(models.Model):
    _name = "fixed.freight_bill.line"
    _description = "freight bill line"

    @api.one
    @api.depends('length_of_the_goods', 'width_of_the_goods')
    def _compute_area(self):
        self.area_of_the_goods = self.length_of_the_goods * self.width_of_the_goods

    @api.one
    @api.depends('unit_price', 'area_of_the_goods')
    def _compute_total_prices(self):
        if self.area_of_the_goods:
            self.total_prices = self.unit_price * self.area_of_the_goods

    freight_id = fields.Many2one('fixed.freight_bill', string='Freight Reference',
                                 ondelete='cascade', index=True)
    product_id = fields.Many2one('product.product', string='产品名称', ondelete='restrict',
                                 required=True, help='Product names that can be customized.'
                                 )
    goods_number = fields.Char(string='货号', help='Mark the number of the goods.')
    length_of_the_goods = fields.Float(string='高度(米)', help='Describe the length of the goods.')
    width_of_the_goods = fields.Float(string='宽度(米)', help='Describe the width of the goods.')
    area_of_the_goods = fields.Float(string='面积(平方米)', store=True, readonly=True, compute='_compute_area',
                                     help="Area of a single item"
                                     )
    unit_price = fields.Float(string='单价(平方米/元)', help='The price of a single item')
    total_prices = fields.Monetary(string='总价', readonly=True, help='The total price of the goods',
                                   compute='_compute_total_prices'
                                   )
    currency_id = fields.Many2one('res.currency', related='freight_id.currency_id', store=True,
                                  related_sudo=False, readonly=False
                                  )
    remark = fields.Text(string='备注')
