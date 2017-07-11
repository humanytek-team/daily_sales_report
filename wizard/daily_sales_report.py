# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2017 Humanytek (<www.humanytek.com>).
#    Manuel Márquez <manuel@humanytek.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class DailySalesReport(models.TransientModel):
    _name = "daily.sales.report"
    _description = "Daily Sales Report"

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        required=True)
    date = fields.Date(string='Date', required=True)

    @api.multi
    def print_daily_sales_report(self):
        """Print report Daily Sales Report"""

        self.ensure_one()
        wizard_data = self.read(['warehouse_id', 'date'])[0]
        SaleOrder = self.env['sale.order']
        sale_orders = SaleOrder.search([
            ('state', '=', 'sale'),
            ('date_order', '<=', wizard_data['date']),
            ('date_order', '>=', wizard_data['date']),
            ('warehouse_id', '=', wizard_data['warehouse_id'][0]),
            ])

        if sale_orders:
            data = dict()
            data['ids'] = sale_orders.mapped('id')
            extra_data = dict()
            extra_data['sales_total'] = sum(sale_orders.mapped('amount_total'))

            payments_done = sale_orders.mapped('invoice_ids').filtered(
                lambda inv: inv.type == 'out_invoice' and
                inv.date_invoice == wizard_data['date']).mapped(
                    'payment_ids').filtered(
                        lambda pay: pay.payment_type == 'inbound' and
                        pay.payment_date == wizard_data['date']
                    )
            payments_done_total = sum(payments_done.mapped('amount'))
            extra_data['payments_done_total'] = payments_done_total

            data['extra_data'] = extra_data

            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'daily_sales_report.report_sales',
                'datas': data,
                }
        else:
            raise ValidationError(
                _('No sales for the warehouse and day selected'))
